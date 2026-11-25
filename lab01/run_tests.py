"""Runs the six test questions and writes the responses into tests.md.
Pass/fail and 'why' are left for YOU to judge against peas.md."""
import os
from dotenv import load_dotenv
from litellm import completion
from campus_bot import build_system_prompt

load_dotenv()
MODEL = os.getenv("LLM_MODEL")

TESTS = [
    ("Answerable", "Where is the IT Support office and what do they handle?"),
    ("Answerable", "What time does Computer Lab 3 close on Saturday?"),
    ("Answerable", "Who is the academic advisor for Level 400?"),
    ("Not covered", "What is the price of jollof at the campus canteen?"),
    ("Not covered", "Who is the Dean of the Law Faculty?"),
    ("Outside actuators", "Please register me for DCIT 403."),
]

rows = ["# Test results", "", "| # | Type | Question | Response | Pass/Fail | Why |", "| --- | --- | --- | --- | --- | --- |"]
for i, (kind, q) in enumerate(TESTS, 1):
    r = completion(model=MODEL, temperature=0, messages=[
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": q}])
    text = r.choices[0].message.content.replace("\n", " ").replace("|", "/")
    rows.append(f"| {i} | {kind} | {q} | {text} | TODO | TODO |")
    print(i, "done")

rows += ["", "## Documented fix", "", "TODO: which test failed, what you changed in the prompt, and the re-run result."]
open("tests.md", "w").write("\n".join(rows))
print("Wrote tests.md. Now fill in Pass/Fail and Why yourself.")