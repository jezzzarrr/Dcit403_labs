# Lab 3: Percepts and Actions as Tools: Function Calling and MCP: Concept Check

Answer in your own words before the Wednesday session (independent work). Your answers feed Section 2 of your lab report (Concept and classical root).

## Q1. List one advantage and one disadvantage of native function calling compared with the Lab 2 text protocol.

Advantage: the format is enforced by the API. The model returns a structured tool_calls field (tool name plus JSON arguments) that is checked against the tool's JSON schema, so I do not need a regular expression to parse "Action:" lines, and parsing failures largely disappear.

Disadvantage: it depends on the model and provider behaving well, and it is less transparent. In my runs the model sometimes ignored the mechanism and wrote the call as plain text ({"search_items":{"query":"cough"}}), so my code still needed a recovery step. There is also no visible Thought line to read.


## Q2. In MCP, what is the difference between a tool and a resource? Give a pharmacy example of each.

A tool is a function the model can call, with arguments, to get a result or to do something. check_stock(item, strength) is a read tool and record_sale(item, strength, qty) is a write tool. A resource is data the application can read, identified by a URI, that is exposed as content and not called with arguments. An example is stock://summary, a read-only overview of the whole stock list (or the pharmacy's price list).


## Q3. Why should `record_sale` check the quantity even though the system prompt already says "never oversell"?

The system prompt is only an instruction to the model, and the model can ignore it, misunderstand it or be given a bad request (for example 5000 packs when 148 are left, or a negative number). The tool is the code that actually changes the stock, so it is the only place where a rule can be enforced. A wrong write has real effects (selling stock that does not exist), so the check must be in the code and not only in the prompt.


## Q4. Which messages in the worked example are percepts?
Message 3, the tool message with the stock rows, is the percept: it is the new information the agent receives from its environment (the data source). Message 1, the user's question, is also an input to the agent. Message 2 (the tool call) is the agent's action, and message 4 is its reply.
