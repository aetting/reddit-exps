OPEN_ENDED ="""I am going to ask you to generate questions and answers about a passage. Here is the passage:

"{text}"

Generate {number} questions that can be answered based on this passage. For each question, the answer should be a short phrase from the passage. Questions should paraphrase and not use the exact words of the passage.

Provide both the question and the answer. Use the format 

Question: ...
Answer: ...
"""

DROP ="""I am going to ask you to generate questions and answers about a passage. Here is the passage:

"{text}"

Generate {number} questions that can be answered based on this passage. Try to questions that require reasoning or calculations over the information in the passage.

Provide both the question and the answer. Use the format 

Question: ...
Answer: ...
"""
