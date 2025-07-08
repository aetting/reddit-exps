OPEN_ENDED ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that are open-ended. Example:

{question_pref}How many legs do dogs have?
{choices_pref}{a_pref}3
{b_pref}4
{c_pref}6
{d_pref}2

{answer_pref}B

Separate ALL questions with "\n%%%%\n".
"""

OPEN_ENDED_NON_MC ="""I will ask you to convert a text into questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that are open-ended. Example:

{question_pref}How many legs do dogs have?

{answer_pref}4

Separate ALL questions with "\n%%%%\n".
"""

STATEMENT_COMPLETION ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that involve completing a statement. DONOT include blanks in the question. Example:

{question_pref}Dogs are mammals with
{choices_pref}{a_pref}Two legs and one tail
{b_pref}Four legs and two tails.
{c_pref}Four legs and one tail.
{d_pref}One leg and four tails.

{answer_pref}C

Separate ALL questions with "\n%%%%\n".
"""

FILL_IN_BLANK ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that contain 2-4 blanks. Example:

{question_pref}Dogs are ___ with ___ legs and ___ tail.
{choices_pref}{a_pref}mammals; four; one
{b_pref}mammals; two; one
{c_pref}amphibians; two; one
{d_pref}amphibians; four; two

{answer_pref}B

Separate ALL questions with "\n%%%%\n".
"""

TWO_STATEMENT ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that contain two statements, with the answers judging whether those statements are true, in the order of the statements. Examples:

{question_pref}Statement 1 | Dogs are mammals. Statement 2 | Dogs have five legs.
{choices_pref}{a_pref}True, True
{b_pref}True, False
{c_pref}False, True
{d_pref}False, False

{answer_pref}B

%%%%

{question_pref}Statement 1 | Paris is the capital of Morocco. Statement 2 | Chicago is a city in Greece.

{choices_pref}{a_pref}True, True
{b_pref}True, False
{c_pref}False, True
{d_pref}False, False

{answer_pref}D

%%%%

{question_pref}Statement 1 | The earth revolves around the sun. Statement 2 | Jupiter's orbit is farther from the sun than the Earth's orbit.

{choices_pref}{a_pref}True, True
{b_pref}True, False
{c_pref}False, True
{d_pref}False, False

{answer_pref}A

Separate ALL questions with "\n%%%%\n".
"""

WHICH_HAS_PROPERTY ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that ask 'which of the following'. Examples:

{question_pref}Which of the following is a mammal?
{choices_pref}{a_pref}Snake
{b_pref}Ostrich
{c_pref}Spider
{d_pref}Dog

{answer_pref}D

%%%%

{question_pref}The capital of France is which of the following cities?
{choices_pref}{a_pref}Athens
{b_pref}Paris
{c_pref}Chicago
{d_pref}Lausanne

{answer_pref}B

Separate ALL questions with "\n%%%%\n".
"""

WHICH_TRUE ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that ask which of the options are true. Examples:

{question_pref}Which of the following is true?
{choices_pref}{a_pref}Snakes are reptiles.
{b_pref}Dogs are mammals.
{c_pref}Both are true.
{d_pref}Neither is true.

{answer_pref}C

%%%%

{question_pref}All of the following are true EXCEPT:
{choices_pref}{a_pref}Athens is the capital of Morocco.
{b_pref}Paris is the capital of France.
{c_pref}Chicago is a city in the US.
{d_pref}Madrid is a city in Spain.

{answer_pref}A

Separate ALL questions with "\n%%%%\n".
"""

IN_QUESTION_OPTIONS ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that provide options within the question and give choices for which options are true. Examples:

{question_pref}Dogs have which of the following properties?

I. They are mammals
II. They have five legs.
III. They have a tail.

{choices_pref}{a_pref}I only
{b_pref}II only
{c_pref}III only
{d_pref}I and III

{answer_pref}D

%%%%

{question_pref}Which of the following are cities in the US?

I. Paris
II. Athens
III. Chicago

{choices_pref}{a_pref}I only
{b_pref}II only
{c_pref}III only
{d_pref}I, II and III

{answer_pref}C

Separate ALL questions with "\n%%%%\n".
"""


######################################################################################################################################################################################################################################

######################################################################################################################################################################################################################################

######################################################################################################################################################################################################################################

OPEN_ENDED_STRUCT ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: First, judge whether this text has information relevant for academic learning, and record this as True or False.

Then convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. 

For format, use open-ended questions. Put the CORRECT option first. Example:

How many legs do dogs have?
A. 3
B. 4
C. 6
D. 2

Answer: B

Give the answer ONLY as "A","B","C" or "D". DONOT include the letter (e.g. "A.") in the options. DONOT reference the text in the question.
"""

FILL_IN_BLANK_STRUCT ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: First, judge whether this text has information relevant for academic learning, and record this as True or False.

Then convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. 

Also, use questions that contain 2-4 blanks. Example:

Question: "Dogs are ___ with ___ legs and ___ tail."
A. mammals; four; one
B. mammals; two; one
C. amphibians; two; one
D. amphibians; four; two

Answer: B

Give the answer ONLY as "A","B","C" or "D". DONOT include the letter (e.g. "A.") in the options. DONOT reference the text in the question.
"""

STATEMENT_COMPLETION_STRUCT ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

# "{text}"

# Instructions: First, judge whether this text has information relevant for academic learning, and record this as True or False.

# Then convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. 

# Also, use questions that involve completing a statement. Example:

# Question: Dogs are mammals with
# A. Two legs and one tail
# B. Four legs and two tails.
# C. Four legs and one tail.
# D. One leg and four tails.

# Answer: C 

# Give the answer ONLY as "A","B","C" or "D". DONOT include the letter (e.g. "A.") in the options. DONOT reference the text in the question.
# """


WHICH_HAS_PROPERTY_STRUCT ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: First, judge whether this text has information relevant for academic learning, and record this as True or False.

Then convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. 

Also, use questions in the form 'which of the following ...'. Example:

Question: Which of the following is a mammal?
A. Snake
B. Ostrich
C. Spider
D. Dog

Answer: D

Give the answer ONLY as "A","B","C" or "D". DONOT include the letter (e.g. "A.") in the options. DONOT reference the text in the question.
"""

STATEMENT_TRUTH_STRUCT =""""{text}"

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




