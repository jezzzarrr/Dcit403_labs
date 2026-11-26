"""MCP client + function-calling agent. The agent never imports the tools: it discovers them
from the server at run time. Every tool call is logged to evidence/tool_calls.jsonl.
Usage:  python client_agent.py          (interactive)
        python client_agent.py --demo   (the six Step 5 questions)"""
import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from litellm import acompletion
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
MODEL = os.getenv("LLM_MODEL") or ""
HERE = Path(__file__).parent
LOG = HERE / "evidence" / "tool_calls.jsonl"
params = StdioServerParameters(command="python", args=[str(HERE / "server.py")])

SYSTEM = ("You are a community-pharmacy stock assistant. Answer ONLY from tool results; never guess stock, "
          "prices or dates. Use record_sale ONLY when the user clearly asks to record a sale; for questions, "
          "use the read tools. If a tool refuses, tell the user why in plain words. "
          "ALWAYS call tools through the tool-calling mechanism; never write a tool call as text or JSON in your reply.")

DEMO = [
    "Do we have amoxicillin 500mg?",
    "Which items expire within 60 days?",
    "What do 2 packs of paracetamol cost?",
    "Is there any cough medicine in stock?",
    "Please record a sale of 2 packs of paracetamol 500mg.",
    "Please record a sale of 5000 packs of paracetamol 500mg.",
]


def log_call(name, args, result, ms, recovered=False):
    LOG.parent.mkdir(exist_ok=True)
    entry = {"timestamp": datetime.now().isoformat(timespec="seconds"), "tool": name, "arguments": args,
             "result_summary": result[:120].replace("\n", " "), "duration_ms": round(ms, 1)}
    if recovered:
        entry["note"] = "model wrote the call as text; recovered by client"
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


async def chat(messages, schemas):
    kwargs = dict(model=MODEL, messages=messages, tools=schemas, temperature=0)
    if "gpt-oss" in MODEL:
        kwargs["reasoning_effort"] = "low"
    for _ in range(4):
        try:
            return await acompletion(**kwargs)
        except Exception as e:
            if "rate_limit" in str(e).lower() or "RateLimit" in str(e):
                m = re.search(r"try again in ([\d.]+)s", str(e))
                await asyncio.sleep((float(m.group(1)) if m else 5) + 1)
                continue
            raise
    raise RuntimeError("rate limit: gave up")


def text_call(text, names):
    """Sometimes the model writes a tool call as plain text, e.g. {"search_items":{"query":"cough"}},
    instead of using the tool_calls field. Detect that and turn it into a real call."""
    t = text.strip().strip("`").strip()
    if t.startswith("json"):
        t = t[4:].strip()
    try:
        d = json.loads(t)
    except Exception:
        return None
    if isinstance(d, dict) and d.get("name") in names and isinstance(d.get("arguments", {}), dict):
        return d["name"], d.get("arguments", {})
    if isinstance(d, dict) and len(d) == 1:
        k, v = next(iter(d.items()))
        if k in names and isinstance(v, dict):
            return k, v
    return None


async def ask(session, schemas, question, max_rounds=6):
    names = {s["function"]["name"] for s in schemas}
    seen = set()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_rounds):
        msg = (await chat(messages, schemas)).choices[0].message
        calls = [(tc.id, tc.function.name, tc.function.arguments or "{}") for tc in (msg.tool_calls or [])]
        recovered = False
        if not calls:
            rec = text_call(msg.content or "", names)
            if not rec:
                return msg.content or ""
            calls = [("recovered_call", rec[0], json.dumps(rec[1]))]   # model wrote the call as text
            recovered = True
        messages.append({"role": "assistant", "content": "" if recovered else (msg.content or ""),
                         "tool_calls": [{"id": cid, "type": "function",
                                         "function": {"name": name, "arguments": raw}}
                                        for cid, name, raw in calls]})
        for cid, name, raw in calls:
            try:
                args = json.loads(raw)
            except Exception:
                args = {}
            start = time.time()
            key = (name, json.dumps(args, sort_keys=True))
            if key in seen:                         # runaway-loop guard: same call twice
                text = "You already made this exact call and have its result. Do not repeat it; answer the user now."
            else:
                seen.add(key)
                try:
                    res = await session.call_tool(name, args)
                    text = "\n".join(c.text for c in res.content if hasattr(c, "text"))
                    if res.isError:
                        text = "ERROR: " + text
                except Exception as e:
                    text = f"ERROR: {e}"
                if not text.strip():                # an empty list comes back as empty text
                    text = "No results found (the tool returned an empty list)."
            ms = (time.time() - start) * 1000
            log_call(name, args, text, ms, recovered)
            print(f"  [tool] {name}({args}) -> {text[:100]!r}" + ("  (recovered from text)" if recovered else ""))
            messages.append({"role": "tool", "tool_call_id": cid, "content": text})
    return "I could not finish within the allowed rounds."


async def main():
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            print("Discovered tools:", [t.name for t in tools])
            schemas = [{"type": "function", "function": {"name": t.name, "description": t.description,
                                                         "parameters": t.inputSchema}} for t in tools]
            if "--demo" in sys.argv:
                for q in DEMO:
                    print(f"\nQ: {q}")
                    print("A:", await ask(session, schemas, q))
                    await asyncio.sleep(5)          # stay under the free per-minute limit
            else:
                while True:
                    q = input("\nYou (quit to exit): ").strip()
                    if q.lower() == "quit":
                        break
                    if q:
                        print("A:", await ask(session, schemas, q))

asyncio.run(main())