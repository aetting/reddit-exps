STANDARD_MC_EVAL="""Question: {question}
A. {opta}
B. {optb}
C. {optc}
D. {optd}
Answer: {answer}"""

GPQA="""Question: {question}
Choices:
(A) {opta}
(B) {optb}
(C) {optc}
(D) {optd}
Answer: ({answer})"""

STANDARD_NON_MC="""Question: {question}
Answer: {answer_full}"""

POPQA_NON_MC="""Q: {question} A: {answer_full}"""

STANDARD_PERIOD_AFLEX="""Question: {question}
A. {opta}
B. {optb}
C. {optc}
D. {optd}
{answer_pref} {answer}"""

STANDARD_PARENS_AFLEX="""Question: {question}
(A) {opta}
(B) {optb}
(C) {optc}
(D) {optd}
{answer_pref} ({answer})"""