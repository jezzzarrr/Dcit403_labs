# Lab 2: Architectures: A ReAct Agent From Scratch: Concept Check

Answer in your own words before the Wednesday session (independent work). Your answers feed Section 2 of your lab report (Concept and classical root).

## Q1. Classify a thermostat, a chess engine and a ReAct agent as reactive, deliberative or hybrid, with one reason each.

Thermostat: reactive. It maps the current temperature directly to an action with a condition-action rule (if the temperature is below the set point, switch the heater on). It has no model of the world, no plan and no memory.

Chess engine: deliberative. It keeps an internal model of the game and searches ahead through possible move sequences to choose a move that serves its goal of winning.

ReAct agent: hybrid. Each step reacts to the latest Observation (reactive layer), while the Thoughts let the model plan across several steps (deliberative layer).


## Q2. In the trace above, which lines are percepts, and which are actions?

Percepts: the user's question and every Observation: line (for example Observation: 1025 and Observation: 175). These are what the agent receives from its environment.

Actions: the Action: lines with their Action Input: (calculator, calculator, finish). These are what the agent does to the environment.

The Thought: lines are neither. They are the agent's internal reasoning (deliberation).


## Q3. Why do we pass `stop=["Observation:"]` when calling the model?

The model only writes text. If it is not stopped, it keeps writing and invents its own Observation: (a made-up tool result) and carries on as if the tool had run. With the stop sequence, the model stops right after its Action Input. My code then runs the real tool and adds the real Observation to the conversation. That keeps the observation true.


## Q4. Map the trace above to the BDI terms belief, desire and intention.

Belief: what the agent holds true: it has GHS 1,200, the prices and quantities, and (after step 1) that the total cost is 1025. Beliefs are updated by each Observation.

Desire: the goal of finding out how much money the trader will have left.

Intention: the plan the agent commits to in its Thought: first compute the total cost, then subtract it from 1200, then use finish to give the answer. Each tool call executes one step of that plan.

