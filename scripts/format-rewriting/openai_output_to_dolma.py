import json
import os
import re
import gzip
import random

def iterate_over_files(input_file_folder):
    outputdir = input_file_folder + "_dolma"
    os.makedirs(outputdir,exist_ok=True)
    for filename in os.listdir(input_file_folder):
        if not '.jsonl' in filename:
            continue
        print(f"\n\nProcessing {filename}\n\n")
        convert_file_to_dolma(filename,input_file_folder,outputdir)


def convert_file_to_dolma(input_filename,input_file_folder,outputdir):
    
    with open(os.path.join(input_file_folder, input_filename)) as f, gzip.open(os.path.join(outputdir,input_filename+".gz"),"wt") as out:
        for line in f:
            d = json.loads(line.strip())
            idx = d["custom_id"]
            response_text = d["response"]["body"]["choices"][0]["message"]["content"]
            parsed_text = response_text.split("%%%%")
            i = 0
            for q_text in parsed_text:
                if not re.match(".*Answer:",q_text,re.DOTALL):
                    continue
                add_q = random.choices([0,1])[0]
                text = q_text.strip()
                if add_q:
                    text = "Question: " + text
                qid = f"{idx}_{i}"
                out_object = {
                    "id":qid,
                    "text":text 
                }
                out.write(json.dumps(out_object) + "\n")
                i += 1

if __name__ == "__main__":
    iterate_over_files("/home/ec2-user/batch_prompts_ht_mini_firsttwo_done")
