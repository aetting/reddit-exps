import json
import os
import re
import gzip
import random
import argparse

import smart_open
import boto3

import multiprocessing as mp

from qa_templates import *

def iterate_over_files(input_file_folder,output_dir, num_processes=1):
    os.makedirs(output_dir,exist_ok=True)

    if "s3://" in input_file_folder:
        client = boto3.client('s3')
        bucket = "ai2-llm"
        s3_prefix = "s3://" + bucket + "/"
        filedir = input_file_folder.replace(s3_prefix,"")
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
        filenames = []
        for page in pages:
            for obj in page["Contents"]:
                okey = obj["Key"]
                if ".jsonl" not in okey:
                    continue
                filenames.append(s3_prefix + okey)
    else:
        filenames = [os.path.join(input_file_folder,f) for f in os.listdir(input_file_folder) if ".jsonl" in f]
    
    with mp.Pool(processes=num_processes) as pool:
        for filename in filenames:
            pool.apply_async(convert_file_to_dolma_diversify, (filename,output_dir))
        pool.close()
        pool.join()


def convert_file_to_dolma(input_filename,outputdir):

    basename = os.path.basename(input_filename)
    print(f"Processing {input_filename}")
    
    with smart_open.open(os.path.join(input_filename)) as f, gzip.open(os.path.join(outputdir,basename+".gz"),"wt") as out:
        for line in f:
            d = json.loads(line.strip())
            idx = d["custom_id"]
            response_text = d["response"]["body"]["choices"][0]["message"]["content"]
            parsed_text = response_text.split("%%%%")
            for i,q_text in enumerate(parsed_text):
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

# format_options = {
#     'q_pref':["Question: ", "Q: ", ""],
#     'a_pref': ["Answer: ", 
#                "A: ", 
#                "The correct answer is ",
#                "Answer is ",
#                "The final answer is "],
#     'choices_pref': [("Choices:\n",.1), ("",.9)],
#     'opt_format': ["period","colon","parens"],
#     'opt_formatb': ["period","parens"]
# }

answer_options = ["Answer:", 
            #    "A:", 
               "The correct answer is",
               "Answer is",
               "The final answer is"]
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

def format_sampling(text):
    qa_distribution = [
        ("STANDARD_MC_EVAL",0),
        ("GPQA", .1),
        ("STANDARD_NON_MC", 0),
        ("POPQA_NON_MC", 0),
        ("STANDARD_PERIOD_AFLEX", .7),
        ("STANDARD_PARENS_AFLEX", .2)
    ]
    tempname_to_temp = {
        "STANDARD_MC_EVAL":STANDARD_MC_EVAL,
        "GPQA":GPQA,
        "STANDARD_NON_MC":STANDARD_NON_MC,
        "POPQA_NON_MC":POPQA_NON_MC,
        "STANDARD_PERIOD_AFLEX":STANDARD_PERIOD_AFLEX,
        "STANDARD_PARENS_AFLEX":STANDARD_PARENS_AFLEX
    }
    letter_to_index = {
        "A": 0,
        "B": 1,
        "C": 2,
        "D": 3
    }
    m = re.match("(.*)\nA.( .*)\nB.(.*)\nC.(.*)\nD.(.*)\n+Answer:(.*)", text, re.DOTALL)
    extracted = [e.strip() for e in m.groups()]
    question,opta,optb,optc,optd,answer = extracted
    tempv,tempp = zip(*qa_distribution)
    template_name = random.choices(tempv,weights = tempp, k=1)[0]
    template = tempname_to_temp[template_name]
    if template_name in ("STANDARD_NON_MC","POPQA_NON_MC"):
        answer_full = [opta,optb,optc,optd][letter_to_index[answer]]
    else:
        answer_full = None

    if template_name in ["STANDARD_PERIOD_AFLEX","STANDARD_PARENS_AFLEX"]:
        answer_pref = random.choices(answer_options)[0]
    else:
        answer_pref = None
    
    # if template_name in 
    # print(text)
    # print("\n\n%%%%%%\n\n")
    new_text = template.format(question=question,opta=opta,optb=optb,optc=optc,optd=optd,answer=answer,answer_full=answer_full,answer_pref=answer_pref)
    # print(template_name)
    # print(new_text)
    return new_text

def convert_file_to_dolma_diversify(input_filename,outputdir):

    basename = os.path.basename(input_filename)
    print(f"Processing {input_filename}")

    random.seed(42)
    
    with smart_open.open(os.path.join(input_filename)) as f, gzip.open(os.path.join(outputdir,basename+".gz"),"wt") as out:
        for line in f:
            d = json.loads(line.strip())
            idx = d["custom_id"]
            response_text = d["response"]["body"]["choices"][0]["message"]["content"]
            parsed_text = response_text.split("%%%%")
            for i,q_text in enumerate(parsed_text):
                if not re.match(".*Answer:",q_text,re.DOTALL):
                    continue
                # add_q = random.choices([0,1])[0]
                text = q_text.strip()
                text = format_sampling(text)
                # if add_q:
                #     text = "Question: " + text
                qid = f"{idx}_{i}"
                out_object = {
                    "id":qid,
                    "text":text 
                }
                out.write(json.dumps(out_object) + "\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",type=int)
    parser.add_argument("--input_dir",type=str)
    parser.add_argument("--output_dir",type=str)
    args = parser.parse_args()

    iterate_over_files(args.input_dir,args.output_dir,num_processes = args.num_processes)
