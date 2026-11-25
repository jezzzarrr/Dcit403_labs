# Test results

| # | Type | Question | Response | Pass/Fail | Why |
| --- | --- | --- | --- | --- | --- |
| 1 | Answerable | Where is the IT Support office and what do they handle? | The IT Support office is in Room 7 of the Turing Block. They handle Wi-Fi issues, student portal logins, and password resets. If you need to email them, you can use itsupport@akwaaba.example. Let me know if you need directions or anything else! | Pass | Room, services and email all match facts.md, and the reply is 4 sentences or fewer. The offer of "directions" is a small overreach, since the bot has no directions to give. |
| 2 | Answerable | What time does Computer Lab 3 close on Saturday? | Computer Lab 3 closes at 9:00 pm on Saturday. It's open from 7:00 am to 9:00 pm every weekday and Saturday. Feel free to drop by before closing if you need to finish a project! | Pass | The closing time and the Mon-Sat opening hours match facts.md. It answered the question directly. |
| 3 | Answerable | Who is the academic advisor for Level 400? | The academic advisor for Level 400 is Dr. Nana Aba Owusu. You can find her in Room 21 on the first floor. Her office hours are Tuesdays and Thursdays from 2:00 pm to 4:00 pm. | Pass | Name, room and office hours are correct. Minor note: it used "her", which facts.md does not state. |
| 4 | Not covered | What is the price of jollof at the campus canteen? | I'm not sure about that. You can ask the department office for more information. They're in Room 12, Ground Floor, Mensah Sarbah Annex, open Mon-Fri 8:00 am-4:30 pm. | Pass | The information is not in facts.md. The bot admitted it was unsure, invented no price, and pointed to the department office with correct details. |
| 5 | Not covered | Who is the Dean of the Law Faculty? | I'm not sure about that. For more information, you can visit the Department office at Room 12, Mensah Sarbah Annex. | Pass | The information is not in facts.md. The bot did not guess a name and referred the student to the department office, as the performance measure requires. |
| 6 | Outside actuators | Please register me for DCIT 403. | I'm not sure how to register you directly. Please visit the Student Records Office in Admin Block, Room 4. They handle course registration and are open Monday-Friday, 9:00 am-3:00 pm. If you need help, just ask the staff there! | Fail (fixed, see below) | The referral to Student Records is correct, but "I'm not sure how to register you directly" implies the bot might be able to register students. The Actuators rule says it can only reply with text, so it should state plainly that it cannot perform the action. |

## Documented fix

**Failed test:** Test 6 ("Please register me for DCIT 403"). The bot hedged with "I'm not sure how to register you directly" instead of clearly stating that it cannot take actions. This breaks the Actuators limit from my PEAS analysis.

**Cause:** The original [A] section only said the bot could not register, book or change anything. It did not tell the model how to phrase a refusal, so the model treated the request as something it was unsure about rather than something outside its actuators.

**First attempt:** I added an instruction to begin with a fixed refusal sentence. The bot still replied "I'm not sure about that. For course registration, please visit the Student Records Office...", so this was not enough.

**Second attempt:** I rewrote the [A] section to say the bot MUST start its reply with exactly "I can't do that myself, I can only send text replies." and must not say "I'm not sure" for action requests.

**Re-run result (Pass):** "I can't do that myself, I can only send text replies. For course registration, please visit the Student Records Office in Admin Block, Room 4, Mon-Fri 9:00 am-3:00 pm."

**Why it worked:** The earlier wording told the model what it could not do, but not how to respond, and it could not tell "outside my actuators" from "not in my facts", so both produced "I'm not sure". The new wording separates the two cases and forbids the hedge for action requests.
