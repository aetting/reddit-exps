import json
import re
import os

from transformers import GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

prompt_dict = {}
full_prompt_dict = {}

def iterate_over_files(input_file_folder):
    orig_total_len = 0
    resp_total_len = 0
    full_prompt_total_len = 0
    prev_prompt = ""
    for filename in os.listdir(input_file_folder):
        if not '.jsonl' in filename:
            continue
        print(f"\n\nProcessing {filename}\n\n")
        file_orig_len, file_resp_len, full_prompt_len = inspect_matched_prompt_response(filename,input_file_folder, prev_prompt)
        orig_total_len += file_orig_len
        resp_total_len += file_resp_len
        full_prompt_total_len += full_prompt_len
    print("TOTAL LENGTHS\n")
    print(f"TOTAL ORIG LEN: {orig_total_len}")
    print(f"TOTAL INPUT PROMPT LEN: {full_prompt_total_len}")
    print(f"TOTAL RESP LEN: {resp_total_len}")

def inspect_matched_prompt_response(input_filename,input_file_folder, prev_prompt):
    
    with open(os.path.join(input_file_folder,input_filename)) as inputf:
        for line in inputf:
            d = json.loads(line.strip())
            idx = d["custom_id"]
            prompt = d["body"]["messages"][1]["content"]
            m = re.match(".*Here is the text:\n\n(.*)Instructions: Convert the information",prompt,re.DOTALL)
            bare_text =  m.groups()[0]
            prompt_dict[idx] = bare_text
            full_prompt_dict[idx] = prompt
    
    orig_total_len = 0
    resp_total_len = 0
    full_prompt_total_len = 0

    with open(os.path.join(input_file_folder + "_done",input_filename)) as f:

        for line in f:
            d = json.loads(line.strip())
            idx = d["custom_id"]
            response_text = d["response"]["body"]["choices"][0]["message"]["content"]
            parsed_text = response_text.split("\n%%%%\n")
            bare_text = prompt_dict[idx]
            fullp_len = len(tokenizer.tokenize(full_prompt_dict[idx]))
            full_prompt_total_len += fullp_len
            if bare_text != prev_prompt:
                print(bare_text)
                bt_len = len(tokenizer.tokenize(prompt_dict[idx]))
                bt_len_w = len(prompt_dict[idx].split())
                orig_total_len += bt_len
                prev_prompt = bare_text
            print("\nQUESTIONS\n")
            resp_len  = 0
            for q_text in parsed_text:
                if not re.match(".*Answer:",q_text,re.DOTALL):
                    continue
                print("~~~Q~~~")
                print(q_text)
                print("\n\n~~~~\n\n")
                q_len = len(tokenizer.tokenize(q_text))
                print(f"QLEN: {q_len}")
                resp_total_len += q_len
                resp_len += q_len
            print(f"ORIG LEN: {bt_len}")
            print(f"ORIG LEN WORDS: {bt_len_w}")
            print(f"RESP LEN: {resp_len}")
            print("\n\n########\n\n")

    return(orig_total_len,resp_total_len,full_prompt_total_len)

if __name__ == "__main__":
    iterate_over_files("/home/ec2-user/test_files_batch_mode_mini")

