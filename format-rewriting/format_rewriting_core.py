import os
import random
import json

from prompt_templates import *

import flex_prompt_templates as flex


def text_to_prompt(text,model):

    distribution = [
        ('OPEN_ENDED',.25),
        ('STATEMENT_COMPLETION',.15),
        ('FILL_IN_BLANK',.15),
        ('TWO_STATEMENT',.05),
        ('WHICH_HAS_PROPERTY',.15),
        ('WHICH_TRUE',.15),
        ('IN_QUESTION_OPTIONS',.1)
    ]
    tempname_to_temp = {
        'OPEN_ENDED': OPEN_ENDED,
        'STATEMENT_COMPLETION': STATEMENT_COMPLETION,
        'FILL_IN_BLANK': FILL_IN_BLANK,
        'TWO_STATEMENT': TWO_STATEMENT,
        'WHICH_HAS_PROPERTY': WHICH_HAS_PROPERTY,
        'WHICH_TRUE': WHICH_TRUE,
        'IN_QUESTION_OPTIONS': IN_QUESTION_OPTIONS
    }

    values,probs = zip(*distribution)

    if model == "gpt-4o": 
        extra = " If the text doesn't contain any information relevant for an academic question, make academic questions inspired by words, phrases, or themes in the text."
    else:
        extra = ""

    template_name = random.choices(values,weights = probs, k=1)[0]
    template = tempname_to_temp[template_name]
    prompt = template.format(text=text,extra=extra)

    return prompt,template_name

format_options = {
    'q_pref':["Question: ", "Q: ", ""],
    'a_pref': ["Answer: ", 
               "A: ", 
               "The correct answer is ",
               "Answer is ",
               "The final answer is "],
    'choices_pref': [("Choices:\n",.1), ("",.9)],
    'opt_format': ["period","colon","parens"],
    'opt_formatb': ["period","parens"]
}

format_options = {
    "base" : ("Question: ","period","Answer: "),
    "simple": ("Q: ", "A: "),
    "gpq": ("Question")
}

option_prefixes = {
    "period" : ("A. ", "B. ", "C. ", "D. "),
    "colon": ("A: ", "B: ", "C: ", "D: "),
    "parens": ("(A) ", "(B) ", "(C) ", "(D) ")
}

def text_to_prompt_diverse(text,model):

    distribution = [
        (flex.OPEN_ENDED,.03),
        (flex.OPEN_ENDED_NON_MC,.18),
        (flex.STATEMENT_COMPLETION,.16),
        (flex.FILL_IN_BLANK,.16),
        (flex.TWO_STATEMENT,.05),
        (flex.WHICH_HAS_PROPERTY,.16),
        (flex.WHICH_TRUE,.16),
        (flex.IN_QUESTION_OPTIONS,.1)
    ]


    values,probs = zip(*distribution)

    if model == "gpt-4o": 
        extra = " If the text doesn't contain any information relevant for an academic question, make academic questions inspired by words, phrases, or themes in the text."
    else:
        extra = ""

    template = random.choices(values,weights = probs, k=1)[0]
    qpref = random.choices(format_options["q_pref"])[0]
    apref = random.choices(format_options["a_pref"])[0]
    cprefv,cprefp = zip(*format_options["choices_pref"])
    cpref = random.choices(cprefv,weights=cprefp)[0]
    opref = random.choices(format_options["opt_format"])[0] if apref != "A: " else random.choices(format_options["opt_formatb"])[0]
    astr,bstr,cstr,dstr = option_prefixes[opref]
    prompt = template.format(text=text,
                             extra=extra,
                             question_pref=qpref,
                             answer_pref=apref,
                             choices_pref=cpref,
                             a_pref=astr,
                             b_pref=bstr,
                             c_pref=cstr,
                             d_pref=dstr
                             )

    return prompt

def write_batch_files(text_iterator,batchfiles_basename,model,outdir,tokenizer):
    total_size_mb = 0
    file_index = 0
    current_file_path = os.path.join(outdir,f"{batchfiles_basename}_f{file_index}.jsonl")
    current_file = open(current_file_path, "w")

    num_written_requests = 0

    for i,(text,text_id) in enumerate(text_iterator):

        prompt,template_name = text_to_prompt(text,model)
        
        text_len = len(tokenizer.tokenize(text))
        max_tokens = round(max(text_len+(.1*text_len),150))
        output_dict = {
            "custom_id": f"{batchfiles_basename}_{i}_{text_id}_{template_name}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                    "model": model, 
                    "messages": [{"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": prompt}
                                ],
                                "max_tokens": max_tokens
                                }
                    }
        json_string = json.dumps(output_dict) + "\n"
        size_in_bytes = len(json_string.encode('utf-8'))  # Get the size in bytes
        size_in_mb = size_in_bytes / (1024 * 1024)
        if (num_written_requests + 1 < 50000) and (total_size_mb + size_in_mb < 200):
            total_size_mb += size_in_mb
            num_written_requests += 1
            current_file.write(json_string)
        else:
            current_file.close()
            print(f"File closed: {current_file_path} (size {total_size_mb}, num_requests {num_written_requests})")

            # Open a new file
            file_index += 1
            current_file_path = os.path.join(outdir,f"{batchfiles_basename}_f{file_index}.jsonl")
            current_file = open(current_file_path, "w")
            current_file.write(json_string)
            total_size_mb = size_in_mb
            num_written_requests = 1
    current_file.close()

if __name__ == "__main__":
    for text in [
        "here is a test",
        "amd another",
        "jere",
        "etetetet",
        "rerererer"
    ]:
        p = text_to_prompt_diverse(text,"gpt")
        print(p)
        print("\n\n&&&&&&&&&&&\n\n")