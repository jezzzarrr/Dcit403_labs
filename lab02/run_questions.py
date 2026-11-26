"""Steps 4 and 5: run the budget question and six more, saving one trace each."""
import time
from react_agent import run_agent

QUESTIONS = [
    "I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil at GHS 95 each. How much will I have left?",
    "What is the capital of the Bono East Region, and what is the total fare for 3 people if a ticket there costs GHS 120 each way (return trip)?",
    "Which Ghanaian region is Tamale the capital of, and how much do 7 trips cost at GHS 85 per trip?",
    "Tell me about the Wikipedia page called 'Zorblax Market Tower of Kumasi'.",
    "Say hello and tell me briefly what you can help with.",
    "rice how much 4 185 and oil 3 95 left from 1200??",
    "I sell 40 bags of rice at GHS 185 each. How many US dollars is that, and what is the capital of the Bono East Region?",
]

for i, q in enumerate(QUESTIONS, 1):
    print(f"\n{'=' * 20} QUESTION {i} {'=' * 20}")
    run_agent(q)
    time.sleep(8)   # stay under the free per-minute token limit