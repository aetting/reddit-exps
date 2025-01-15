OPEN_ENDED ="""
"{text}"

First, judge whether this text has information relevant for academic learning, and record this as True or False.

Take the educational information from the text and create multiple choice questions using that information. Use open-ended questions. Example:

Question: How many legs do dogs have?
A. 3
B. 4
C. 6
D. 2

Answer: B

Give the answer as "A","B","C" or "D". DONOT include the letter (e.g. "A.") in the options. DONOT reference the text in the question.
"""

FILL_IN_BLANK ="""
"{text}"

First, judge whether this text has information relevant for academic learning, and record this as True or False.

Take the educational information from the text and create multiple choice questions using that information. Use questions that contain 2-4 blanks. Example:

Question: "Dogs are ___ with ___ legs and ___ tail."
A. mammals; four; one
B. mammals; two; one
C. amphibians; two; one
D. amphibians; four; two

Answer: B

Give the answer as "A","B","C" or "D". DONOT include the letter (e.g. "A.") in the options. DONOT reference the text in the question.
"""

STATEMENT_COMPLETION ="""
"{text}"

First, judge whether this text has information relevant for academic learning, and record this as True or False.

Take the educational information from the text and create multiple choice questions using that information. Use questions that involve completing a statement. Example:

Question: Dogs are mammals with
A. Two legs and one tail
B. Four legs and two tails.
C. Four legs and one tail.
D. One leg and four tails.

Answer: C 


Give the answer as "A","B","C" or "D". DONOT include the letter (e.g. "A.") in the options. DONOT reference the text in the question.
"""

STATEMENT_TRUTH =""""{text}"

First, judge whether this text has information relevant for academic learning, and record this as True or False.

Take the educational information from the text and create a list of true statements and a list of false statements. Do not reference the text in the statements.
"""

OLD_TRUTH="""multiple choice questions using that information. Create questions that involve judging the truth of statements. The statements can be true or false.

Example question: Statement 1 | Dogs are mammals. Statement 2 | Dogs have five legs.

These should be the answer options: 
A. True, True
B. True, False
C. False, True
D. False, False

Then give the answer based on the truth of the statements. For example, if both statements in the question are False, choose "D". If the first statement is True and the second statement is False, choose "B".


DONOT include the letter (e.g. "A.") in the options. DONOT reference the text in the question.
"""




