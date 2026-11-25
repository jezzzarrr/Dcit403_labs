# Lab 1: Agents Then and Now: PEAS and Your First LLM Call: Concept Check

Answer in your own words before the Wednesday session (independent work). Your answers feed Section 2 of your lab report (Concept and classical root).

## Q1. Give the PEAS description of a self-checkout machine at a supermarket.

PEAS	Self-checkout machine
Performance	- Every item is scanned and priced correctly; the total is right; payment succeeds; checkout is fast; theft and scanning errors are caught; the customer can finish without waiting for staff.

Environment	- The checkout area of a supermarket: the customer, the items, the bagging area, the store's price database, and the attendant who can be called.

Actuators - Touchscreen display, speaker (beeps and voice prompts), receipt printer, payment terminal and cash handler, a flag or light to call staff.

Sensors	- Barcode scanner, weighing scale in the bagging area, touchscreen taps, card or mobile money reader, sometimes a camera.

## Q2. Is the Campus Info Bot's environment episodic or sequential? Justify your answer using what the bot needs to remember.

It is sequential. The bot's current action depends on what was said earlier in the conversation. In my five-turn chat, "What do they handle?" and "What is their email?" only made sense because the bot remembered from turn 1 that we were talking about IT Support, and the last question needed both earlier offices. If the environment were episodic, each question would be independent and the bot would not need to remember anything. Because it is sequential, the bot has to keep the conversation history and send it to the model each turn.


## Q3. Which part of an LLM agent plays the role of the percept sequence?

The conversation history, which is the list of messages (the user's messages and the model's replies) that is sent to the model on every turn. In campus_bot.py this is the history list. The model itself has no memory between calls, so this list is the percept sequence the agent function uses to choose its next action.


## Q4. An agent gives a wrong office location because its facts block was out of date. Was it irrational? Explain.

No. A rational agent chooses the action expected to maximise its performance measure given its percept sequence and its built-in knowledge. Rational does not mean all-knowing. If the facts block was out of date, the agent acted correctly on the knowledge it had, so the fault is in the knowledge it was given and not in its decision. The fix is to keep the facts file up to date (which is why facts.md is loaded on every turn). The agent could only be called irrational if it ignored the facts it had or invented something instead.

