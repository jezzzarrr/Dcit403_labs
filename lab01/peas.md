# PEAS: Campus Info Bot ("Kofi the Campus Guide")

| PEAS | Campus Info Bot |
| --- | --- |
| Performance | Answers only from the facts file; admits when it does not know and points to the department office; never invents room numbers or times; replies are short (max ~4 sentences); stays polite; never claims to have done an action. |
| Environment | New students typing in a terminal; a facts.md file of office information; the department office as a human fallback. |
| Actuators | Print a text reply only (cannot register, book, email or change anything). |
| Sensors | The student's typed messages; the conversation history; the facts block loaded from facts.md. |

## Environment properties
| Property | Classification | Why |
| --- | --- | --- |
| Observability | Partially observable | It sees only typed text, not the student's year, programme or real intent. It must ask if the question is unclear. |
| Determinism | Stochastic | Students ask unpredictable things, and the model's output varies between runs. |
| Episodic / sequential | Sequential | Follow-ups like "and when does it close?" depend on earlier turns. |
| Static / dynamic | Static during a chat | Facts do not change while the student is typing (the facts file can change between sessions). |
| Discrete / continuous | Discrete | Turns of text, a finite set of offices and times. |
| Single / multi-agent | Single-agent (arguably multi) | Only the bot and one student per chat; the student is treated as part of the environment. |