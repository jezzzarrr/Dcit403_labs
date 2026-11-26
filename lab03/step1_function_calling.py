"""Step 1: native function calling with one plain Python function (no MCP yet)."""
import csv
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from litellm import completion

load_dotenv()
MODEL = os.getenv("LLM_MODEL")
DATA = Path(__file__).parent / "data" / "pharmacy_stock.csv"


def check_stock(item: str, strength: str = ""):
    with open(DATA, newline="") as f:
        rows = [r for r in csv.DictReader(f) if item.lower() in r["item"].lower()]
    if strength:
        rows = [r for r in rows if strength.lower() in r["strength"].lower()]
    return rows


TOOLS = {"check_stock": check_stock}
tool_schemas = [{"type": "function", "function": {
    "name": "check_stock",
    "description": "Look up pharmacy stock rows by medicine name and optional strength, e.g. item='amoxicillin', strength='500mg'.",
    "parameters": {"type": "object",
                   "properties": {"item": {"type": "string", "description": "Medicine name or part of it"},
                                  "strength": {"type": "string", "description": "Optional strength such as 500mg"}},
                   "required": ["item"]}}}]

messages = [{"role": "system", "content": "You are a pharmacy stock assistant. Use the tools; never guess stock."},
            {"role": "user", "content": "Do we have amoxicillin 500mg?"}]

resp = completion(model=MODEL, messages=messages, tools=tool_schemas, temperature=0)
msg = resp.choices[0].message
print("MODEL ASKED FOR:", [(tc.function.name, tc.function.arguments) for tc in (msg.tool_calls or [])])

messages.append({"role": "assistant", "content": msg.content or "",
                 "tool_calls": [{"id": tc.id, "type": "function",
                                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                                for tc in (msg.tool_calls or [])]})
for tc in msg.tool_calls or []:
    args = json.loads(tc.function.arguments)
    result = TOOLS[tc.function.name](**args)
    print("TOOL RESULT:", result)
    messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})

resp = completion(model=MODEL, messages=messages, tools=tool_schemas, temperature=0)
print("FINAL ANSWER:", resp.choices[0].message.content)