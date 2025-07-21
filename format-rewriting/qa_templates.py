STANDARD_MC_EVAL="""Question: {question}
A. {opta}
B. {optb}
C. {optc}
D. {optd}
Answer: {answer}. {answer_full}"""

GPQA="""Question: {question}
Choices:
(A) {opta}
(B) {optb}
(C) {optc}
(D) {optd}
Answer: ({answer}) {answer_full}"""

STANDARD_PERIOD_AFLEX="""Question: {question}
A. {opta}
B. {optb}
C. {optc}
D. {optd}
{answer_pref} {answer}. {answer_full}"""

STANDARD_PARENS_AFLEX="""Question: {question}
(A) {opta}
(B) {optb}
(C) {optc}
(D) {optd}
{answer_pref} ({answer}) {answer_full}"""

STANDARD_NON_MC="""Question: {question}
Answer: {answer_full}"""

POPQA_NON_MC="""Q: {question} A: {answer_full}"""

STANDARD_NON_MC_PSG="""Passage: {orig_text}
Question: {question}
Answer: {answer_full}"""