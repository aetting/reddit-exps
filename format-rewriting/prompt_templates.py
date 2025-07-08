OPEN_ENDED ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that are open-ended. Example:

Question: How many legs do dogs have?
A. 3
B. 4
C. 6
D. 2

Answer: B

Separate ALL questions with "\n%%%%\n".
"""

STATEMENT_COMPLETION ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that involve completing a statement. DONOT include blanks in the question. Example:

Question: Dogs are mammals with
A. Two legs and one tail
B. Four legs and two tails.
C. Four legs and one tail.
D. One leg and four tails.

Answer: C

Separate ALL questions with "\n%%%%\n".
"""

FILL_IN_BLANK ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that contain 2-4 blanks. Example:

Question: Dogs are ___ with ___ legs and ___ tail.
A. mammals; four; one
B. mammals; two; one
C. amphibians; two; one
D. amphibians; four; two

Answer: B

Separate ALL questions with "\n%%%%\n".
"""

TWO_STATEMENT ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that contain two statements, with the answers judging whether those statements are true, in the order of the statements. Examples:

Question: Statement 1 | Dogs are mammals. Statement 2 | Dogs have five legs.
A. True, True
B. True, False
C. False, True
D. False, False

Answer: B

%%%%

Question: Statement 1 | Paris is the capital of Morocco. Statement 2 | Chicago is a city in Greece.

A. True, True
B. True, False
C. False, True
D. False, False

Answer: D

%%%%

Question: Statement 1 | The earth revolves around the sun. Statement 2 | Jupiter's orbit is farther from the sun than the Earth's orbit.

A. True, True
B. True, False
C. False, True
D. False, False

Answer: A

Separate ALL questions with "\n%%%%\n".
"""

WHICH_HAS_PROPERTY ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that ask 'which of the following'. Examples:

Question: Which of the following is a mammal?
A. Snake
B. Ostrich
C. Spider
D. Dog

Answer: D

%%%%

Question: The capital of France is which of the following cities?
A. Athens
B. Paris
C. Chicago
D. Lausanne

Answer: B

Separate ALL questions with "\n%%%%\n".
"""

WHICH_TRUE ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that ask which of the options are true. Examples:

Question: Which of the following is true?
A. Snakes are reptiles.
B. Dogs are mammals.
C. Both are true.
D. Neither is true.

Answer: C

%%%%

Question: All of the following are true EXCEPT:
A. Athens is the capital of Morocco.
B. Paris is the capital of France.
C. Chicago is a city in the US.
D. Madrid is a city in Spain.

Answer: A

Separate ALL questions with "\n%%%%\n".
"""

IN_QUESTION_OPTIONS ="""I will ask you to convert a text into multiple-choice questions. Here is the text:

"{text}"

Instructions: Convert the information in the text into academic multiple choice questions. ONLY include questions that are academic. DONOT reference the text in the question.{extra}

For format, use questions that provide options within the question and give choices for which options are true. Examples:

Question: Dogs have which of the following properties?

I. They are mammals
II. They have five legs.
III. They have a tail.

A. I only
B. II only
C. III only
D. I and III

Answer: D

%%%%

Question: Which of the following are cities in the US?

I. Paris
II. Athens
III. Chicago

A. I only
B. II only
C. III only
D. I, II and III

Answer: C

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




