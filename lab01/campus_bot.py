"""Campus Info Bot: 'Kofi the Campus Guide'.
Every section of the system prompt is tagged with the PEAS letter it came from,
so the prompt can be traced back to peas.md. Facts live in facts.md and are
reloaded every turn, so they can change without touching the code."""
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from litellm import completion

load_dotenv()
MODEL = os.getenv("LLM_MODEL")
HERE = Path(__file__).parent

# One prompt section per PEAS letter.
PROMPT_P = """[P: Performance measure -> rules]
- Answer ONLY from the FACTS block below.
- If the answer is not in the facts, say you are not sure and send the student to the Department office (Room 12, Mensah Sarbah Annex).
- Never invent room numbers, times, names or emails.
- Keep replies to 4 sentences or fewer, in a warm, friendly tone."""

PROMPT_E = """[E: Environment -> role and facts]
You are Kofi, a friendly campus guide for new Computer Science students.
You chat with students in a terminal, one question at a time.
FACTS (your only source of truth):
{facts}"""

PROMPT_A = """[A: Actuators -> limits]
You can ONLY reply with text. You cannot register, book, email, pay or change anything.
If the student asks you to do any action (register, book, email, pay, change something), you MUST start your reply with exactly this sentence: "I can't do that myself, I can only send text replies." Do not say "I'm not sure" for these requests. After that sentence, tell the student who can help, using the facts."""

PROMPT_S = """[S: Sensors -> what you can perceive]
You only see this conversation. You cannot see student records or the student's account.
If a question is unclear, ask ONE short clarifying question."""


def build_system_prompt() -> str:
    facts = (HERE / "facts.md").read_text()  # re-read each turn
    return "\n\n".join([PROMPT_E.format(facts=facts), PROMPT_P, PROMPT_A, PROMPT_S])


def main():
    if not MODEL:
        print("LLM_MODEL is not set. Copy .env.example to .env first.")
        return
    history = []  # the percept sequence
    print("Kofi the Campus Guide. Commands: /prompt (show system prompt), /turns, quit")
    while True:
        user = input("\nYou: ").strip()
        if user.lower() == "quit":
            break
        if user == "/prompt":
            print(build_system_prompt())
            continue
        if user == "/turns":
            print(f"Percepts so far: {len([m for m in history if m['role'] == 'user'])} user messages")
            continue
        if not user:
            continue
        history.append({"role": "user", "content": user})
        messages = [{"role": "system", "content": build_system_prompt()}] + history
        start = time.time()
        stream = completion(model=MODEL, messages=messages, temperature=0, stream=True)
        print("Kofi: ", end="", flush=True)
        reply = ""
        for chunk in stream:
            piece = chunk.choices[0].delta.content or ""
            reply += piece
            print(piece, end="", flush=True)
        print(f"\n[{time.time() - start:.1f}s]")
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()