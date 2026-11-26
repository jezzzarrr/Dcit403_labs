"""Step 1: the model on its own, no tools. Writes evidence/baseline.md.
The auto-check only looks for the expected text; YOU confirm each row by reading the answer."""
import os
from pathlib import Path
from dotenv import load_dotenv
from litellm import completion

load_dotenv()
MODEL = os.getenv("LLM_MODEL")
BUDGET = ("I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil "
          "at GHS 95 each. How much will I have left?")
FACTS = [("What is the capital of the Bono East Region of Ghana?", "Techiman"),
         ("In which year did Ghana become independent?", "1957")]

def ask(q):
    r = completion(model=MODEL, temperature=1, messages=[{"role": "user", "content": q}])
    return r.choices[0].message.content.strip()

rows = ["# Baseline: the model alone (no tools)", "",
        "| # | Question | Answer | Expected | Auto-check | My verdict |", "| --- | --- | --- | --- | --- | --- |"]
n = 1
for _ in range(3):
    a = ask(BUDGET)
    rows.append(f"| {n} | Budget question | {a.replace(chr(10), ' ').replace('|', '/')} | GHS 175 | {'175' in a} | TODO |")
    n += 1
for q, exp in FACTS:
    a = ask(q)
    rows.append(f"| {n} | {q} | {a.replace(chr(10), ' ').replace('|', '/')} | {exp} | {exp in a} | TODO |")
    n += 1
Path(__file__).parent.joinpath("evidence", "baseline.md").write_text("\n".join(rows))
print("Wrote evidence/baseline.md. Read each answer and fill in 'My verdict' (correct/incorrect).")