"""Offline test of the loop with a scripted fake model (no API needed).
Shows the three required failure paths: unparseable reply, unknown action, max_steps."""
from react_agent import run_agent

def scripted(replies):
    it = iter(replies)
    return lambda messages: (next(it), 10)

print("### 1. unparseable reply, then unknown action, then recovery")
run_agent("test 1", llm=scripted([
    "I think the answer is 175.",
    "Thought: check weather\nAction: weather\nAction Input: Accra",
    "Thought: compute\nAction: calculator\nAction Input: 1200 - 1025",
    "Thought: done\nAction: finish\nAction Input: GHS 175 left",
]), save=False)

print("\n### 2. runaway loop hits max_steps")
run_agent("test 2", max_steps=3, llm=lambda m: ("Thought: again\nAction: calculator\nAction Input: 1+1", 10), save=False)

print("\n### 3. unsafe calculator input")
run_agent("test 3", llm=scripted([
    "Thought: x\nAction: calculator\nAction Input: __import__('os').system('ls')",
    "Thought: done\nAction: finish\nAction Input: refused",
]), save=False)