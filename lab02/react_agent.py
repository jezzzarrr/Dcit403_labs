"""ReAct agent from scratch: Thought -> Action -> Observation, in plain Python."""
import json
import os
import re
import time
from pathlib import Path
from tools import TOOLS

HERE = Path(__file__).parent
EVIDENCE = HERE / "evidence"

SYSTEM = """You are "Maame Makola", a quick, careful helper for traders at Makola Market.
You solve problems step by step using the actions below. You NEVER do arithmetic yourself and you NEVER invent facts.

ACTIONS
- calculator: evaluates arithmetic. Input: an expression such as 4*185 + 3*95
- wiki_lookup: Wikipedia summary. Input: a page title such as Techiman
- convert_currency: fixed lab rates. Input: amount, FROM, TO such as 7400, GHS, USD
- finish: give the final answer to the trader. Input: the answer text

On EVERY step reply in exactly this format and nothing else:
Thought: <your reasoning>
Action: calculator | wiki_lookup | convert_currency | finish
Action Input: <input for the tool, or the final answer if finish>

After an Action you will receive an Observation. Wait for it. Use finish as soon as you can answer.
IMPORTANT: write plain text only, in the format above. Do NOT use function calling or JSON."""

ACTION_RE = re.compile(r"Action:\s*(\w+)\s*\nAction Input:\s*(.*)", re.DOTALL)


def parse(text):
    m = ACTION_RE.search(text)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


def llm_call(messages):
    """Model call. Returns (text, total_tokens). stop=['Observation:'] stops the model from
    inventing its own observations. Handles rate limits and the odd output formats that
    gpt-oss on Groq sometimes produces."""
    from dotenv import load_dotenv
    from litellm import completion
    load_dotenv()
    model = os.getenv("LLM_MODEL") or ""
    kwargs = dict(model=model, messages=messages, temperature=0, stop=["Observation:"])
    if "gpt-oss" in model:
        kwargs["reasoning_effort"] = "low"          # fewer hidden tokens, fewer rate-limit hits
    for _ in range(4):
        try:
            r = completion(**kwargs)
            return r.choices[0].message.content or "", r.usage.total_tokens
        except Exception as e:
            err = str(e)
            if "rate_limit" in err.lower() or "RateLimit" in err:
                m = re.search(r"try again in ([\d.]+)s", err)
                time.sleep((float(m.group(1)) if m else 5) + 1)
                continue
            text = recover_failed_generation(err)
            if text is None:
                raise
            return text, 0
    raise RuntimeError("rate limit: gave up after 4 tries")


def _as_text(name, args):
    if isinstance(args, dict):
        value = args.get("Action Input") if name == "finish" else None
        if value is None:                           # several arguments -> "7400, GHS, USD"
            value = ", ".join(str(v) for v in args.values())
    else:
        value = args
    return (f"Thought: (the model made a native tool call; converted to text)\n"
            f"Action: {name}\nAction Input: {value}")


def recover_failed_generation(err: str):
    """Groq rejects some replies ('tool_use_failed', 'output_parse_failed') but includes what the
    model wrote in 'failed_generation'. Turn it back into our text format when possible; if it is
    just plain text, return it as is so the parser rejects it and a corrective Observation is sent."""
    try:
        body, _ = json.JSONDecoder().raw_decode(err[err.index('{"error"'):])
        fg = body["error"].get("failed_generation")
    except Exception:
        return None
    if not fg:
        return None
    try:                                            # a well-formed native call
        call = json.loads(fg)
        return _as_text(call["name"], call.get("arguments", {}))
    except Exception:
        pass
    if fg.lstrip().startswith('{"name"'):           # a malformed native call
        m = re.search(r'"arguments":\s*(.*)\}\s*$', fg, re.DOTALL)
        n = re.search(r'"name":\s*"([^"]*)"', fg)
        if m and n:
            raw = m.group(1).strip()
            return raw if "Action:" in raw else _as_text(n.group(1), raw)
    return fg


def next_trace_path():
    EVIDENCE.mkdir(exist_ok=True)
    n = len(list(EVIDENCE.glob("trace_*.txt"))) + 1
    return EVIDENCE / f"trace_{n}.txt"


def run_agent(question, max_steps=6, llm=llm_call, save=True):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": question}]
    trace = [f"QUESTION: {question}", ""]
    tokens = 0
    answer = None

    for step in range(1, max_steps + 1):
        try:
            text, used = llm(messages)
        except Exception as e:                      # API down, bad key, rate limit...
            trace.append(f"[step {step}] MODEL ERROR: {e}")
            answer = "Sorry, I could not reach the model."
            break
        tokens += used
        trace.append(f"--- step {step} ---\n{text.strip()}")
        messages.append({"role": "assistant", "content": text})

        action, action_input = parse(text)
        if action is None:                          # unparseable reply -> corrective Observation
            obs = ("Observation: Your reply was not in the required format. Reply with exactly:\n"
                   "Thought: ...\nAction: calculator | wiki_lookup | convert_currency | finish\n"
                   "Action Input: ...")
        elif action == "finish":
            answer = action_input
            break
        elif action not in TOOLS:                   # unknown tool -> corrective Observation
            obs = (f"Observation: Unknown action '{action}'. "
                   f"Valid actions are: {', '.join(TOOLS)}, finish.")
        else:
            obs = "Observation: " + TOOLS[action](action_input)
        trace.append(obs)
        messages.append({"role": "user", "content": obs})

    if answer is None:                              # reached max_steps (or model error handled above)
        answer = f"I could not finish within {max_steps} steps."
        trace.append(f"[stopped: max_steps={max_steps} reached]")

    trace += ["", f"FINAL ANSWER: {answer}", f"TOTAL TOKENS: {tokens}"]
    out = "\n".join(trace)
    if save:
        path = next_trace_path()
        path.write_text(out)
        out += f"\n[saved to {path.name}]"
    print(out)
    return answer


if __name__ == "__main__":
    q = input("Ask Maame Makola: ")
    run_agent(q)