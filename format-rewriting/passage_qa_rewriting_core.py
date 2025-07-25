import os
import random
import json

from psg_qa_prompt_templates import *

def text_to_prompt(text,model):
    distribution = [
        (DEFAULT,.1),
        (SPAN,.25),
        (PPHRASE,.25),
        (DROP,.4),
        # (DROPR,.2)
    ]
    values,probs = zip(*distribution)

    # if model == "gpt-4o": 
    #     extra = " If the text doesn't contain any information relevant for an academic question, make academic questions inspired by words, phrases, or themes in the text."
    # else:
    #     extra = ""

    template = random.choices(values,weights = probs, k=1)[0]
    qnum_prop = round(len(text.split())/40)
    if qnum_prop < 2:
        qnum = 1
    else:
        qnum = max(1,min(8,random.choices(range(qnum_prop-4,qnum_prop))[0]))
    num_quest = f"{qnum} questions" if qnum > 1 else "1 question"
    prompt = template.format(text=text,num_quest=num_quest)

    return prompt

def write_batch_files(text_iterator,batchfiles_basename,model,outdir,tokenizer):
    total_size_mb = 0
    file_index = 0
    current_file_path = os.path.join(outdir,f"{batchfiles_basename}_f{file_index}.jsonl")
    current_file = open(current_file_path, "w")

    num_written_requests = 0

    random.seed(42)

    for i,(text,text_id) in enumerate(text_iterator):

        # print(text_id)
        # print(text)
        # print("\n%%%%\n")
        prompt = text_to_prompt(text,model)
        # print(prompt)
        
        text_len = len(tokenizer.tokenize(text))
        # max_tokens = round(max(text_len+(.1*text_len),150))
        max_tokens=500
        output_dict = {
            "custom_id": f"f{batchfiles_basename}_p{i}_w{text_id}",
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
        if (num_written_requests + 1 < 1000) and (total_size_mb + size_in_mb < 200):
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