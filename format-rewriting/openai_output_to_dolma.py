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

def iterate_over_files(input_file_folder,output_dir, num_processes=1,orig_texts_dir=None):
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
    
    convert_file_to_dolma_non_mc(filenames[0],output_dir,mcplus=False,orig_texts_dir=orig_texts_dir)
    with mp.Pool(processes=num_processes) as pool:
        for filename in filenames:
            pool.apply_async(convert_file_to_dolma_non_mc, (filename,output_dir,False,orig_texts_dir))
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
               "The final answer is",
               "The answer is"]
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

def format_sampling(match_object):
    qa_distribution = [
        ("STANDARD_MC_EVAL",0),
        ("GPQA", .1),
        ("STANDARD_NON_MC", 0),
        ("POPQA_NON_MC", 0),
        ("STANDARD_PERIOD_AFLEX", .7),
        ("STANDARD_PARENS_AFLEX", .2)
    ]
    extracted = [e.strip() for e in match_object.groups()]
    question,opta,optb,optc,optd,answer = extracted
    tempv,tempp = zip(*qa_distribution)
    template_name = random.choices(tempv,weights = tempp, k=1)[0]
    template = tempname_to_temp[template_name]
    # if template_name in ("STANDARD_NON_MC","POPQA_NON_MC"):
    #     answer_full = [opta,optb,optc,optd][letter_to_index[answer]]
    # else:
    #     answer_full = None

    if template_name in ["STANDARD_PERIOD_AFLEX","STANDARD_PARENS_AFLEX"]:
        answer_pref = random.choices(answer_options)[0]
    else:
        answer_pref = None
    
    new_text = template.format(question=question,opta=opta,optb=optb,optc=optc,optd=optd,answer=answer,answer_full=answer_full,answer_pref=answer_pref)
    return new_text,template_name


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
                m = re.match("(.*)\nA.( .*)\nB.(.*)\nC.(.*)\nD.(.*)\n+Answer:(.*)", text, re.DOTALL)
                if m is not None:
                    text,template_name = format_sampling(m)
                else:
                    text = text
                    template_name = "ORIG"
                # if add_q:
                #     text = "Question: " + text
                qid = f"{idx}_{i}_{template_name}"
                out_object = {
                    "id": qid,
                    "text": text 
                }
                out.write(json.dumps(out_object) + "\n")

def get_orig_dict(filename,filedir):
    origdict = {}
    basename = os.path.basename(filename)
    m = re.match("(.*)_f[0-9].jsonl",basename)
    orig_filename = m.groups()[0] + ".json.gz"
    with smart_open.open(os.path.join(filedir,orig_filename)) as f:
        for line in f:
            d = json.loads(line)
            origdict[d["id"]] = d ["text"]
    return origdict

def make_non_mc(match_object):
    qa_distribution = [
        ("STANDARD_NON_MC", .7),
        ("POPQA_NON_MC", .3),
    ]
    extracted = [e.strip() for e in match_object.groups()]
    # print(extracted)
    question,opta,optb,optc,optd,answer = extracted
    tempv,tempp = zip(*qa_distribution)
    template_name = random.choices(tempv,weights = tempp, k=1)[0]
    template = tempname_to_temp[template_name]
    # if template_name in ("STANDARD_NON_MC","POPQA_NON_MC"):
    answer_full = [opta,optb,optc,optd][letter_to_index[answer]]

    new_text = template.format(question=question,answer_full=answer_full)

    return new_text,template_name

def non_mc_with_context(match_object,orig_text):
    # qa_distribution = [
    #     ("STANDARD_NON_MC", .7),
    #     ("POPQA_NON_MC", .3),
    # ]
    extracted = [e.strip() for e in match_object.groups()]
    # print(extracted)
    question,opta,optb,optc,optd,answer = extracted
    # tempv,tempp = zip(*qa_distribution)
    # template_name = random.choices(tempv,weights = tempp, k=1)[0]
    # template = tempname_to_temp[template_name]
    # if template_name in ("STANDARD_NON_MC","POPQA_NON_MC"):
    template_name = "STANDARD_NON_MC_PSG"
    template = STANDARD_NON_MC_PSG
    answer_full = [opta,optb,optc,optd][letter_to_index[answer]]

    new_text = template.format(question=question,answer_full=answer_full,orig_text=orig_text)
    # import pdb; pdb.set_trace()

    return new_text,template_name

def mc_plus_full_answer(match_object):
    qa_distribution = [
        ("STANDARD_MC_EVAL",0),
        ("GPQA", .1),
        ("STANDARD_NON_MC", 0),
        ("POPQA_NON_MC", 0),
        ("STANDARD_PERIOD_AFLEX", .7),
        ("STANDARD_PARENS_AFLEX", .2)
    ]
    extracted = [e.strip() for e in match_object.groups()]
    question,opta,optb,optc,optd,answer = extracted
    tempv,tempp = zip(*qa_distribution)
    template_name = random.choices(tempv,weights = tempp, k=1)[0]
    template = tempname_to_temp[template_name]
    # if template_name in ("STANDARD_NON_MC","POPQA_NON_MC"):
    #     answer_full = [opta,optb,optc,optd][letter_to_index[answer]]
    # else:
    #     answer_full = None
    answer_full = [opta,optb,optc,optd][letter_to_index[answer]]
    if template_name in ["STANDARD_PERIOD_AFLEX","STANDARD_PARENS_AFLEX"]:
        answer_pref = random.choices(answer_options)[0]
    else:
        answer_pref = None
    
    new_text = template.format(question=question,opta=opta,optb=optb,optc=optc,optd=optd,answer=answer,answer_full=answer_full,answer_pref=answer_pref)
    return new_text,template_name


def convert_file_to_dolma_non_mc(input_filename,outputdir,mcplus=False,orig_texts_dir=None):

    basename = os.path.basename(input_filename)
    print(f"Processing {input_filename}")

    random.seed(42)

    if orig_texts_dir is not None:
        orig_id_dict = get_orig_dict(input_filename,orig_texts_dir)
    
    with smart_open.open(os.path.join(input_filename)) as f, gzip.open(os.path.join(outputdir,basename+".gz"),"wt") as out:
        for line in f:
            d = json.loads(line.strip())
            idx = d["custom_id"]
            print(idx)
            idm = re.match(".*-[0-9]+_[0-9]+_([0-9a-zA-Z]+_[0-9a-zA-Z]+)_(.*)",idx) 
            prompt_temp = '_'.join(idm.groups()[1].split("_"))
            orig_id = idm.groups()[0]
            if orig_texts_dir is not None:
                orig_text = orig_id_dict[orig_id]
            # prompt_temp = idm.groups()[0].split("_")[-1]
            if prompt_temp not in ["OPEN_ENDED","STATEMENT_COMPLETION"]:
                continue
            response_text = d["response"]["body"]["choices"][0]["message"]["content"]
            parsed_text = response_text.split("%%%%")
            for i,q_text in enumerate(parsed_text):
                if not re.match(".*Answer:",q_text,re.DOTALL):
                    continue
                # add_q = random.choices([0,1])[0]
                text = q_text.strip()
                m = re.match("Question:(.*)\nA.( .*)\nB.(.*)\nC.(.*)\nD.(.*)\n+Answer:\s*([ABCD])", text, re.DOTALL)
                if mcplus:
                    if m is not None:
                        text,template_name = mc_plus_full_answer(m)
                elif orig_texts_dir is not None:
                    if m is not None:
                        text,template_name = non_mc_with_context(m,orig_text)
                else:
                    if m is not None:
                        text,template_name = make_non_mc(m)
                # else:
                #     text = text
                #     template_name = "ORIG"
                # if add_q:
                #     text = "Question: " + text
                qid = f"{idx}_{i}_{template_name}"
                out_object = {
                    "id": qid,
                    "text": text 
                }
                out.write(json.dumps(out_object) + "\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",type=int,default=1)
    parser.add_argument("--input_dir",type=str)
    parser.add_argument("--output_dir",type=str)
    parser.add_argument("--orig_texts_dir",type=str,default=None)
    args = parser.parse_args()

    iterate_over_files(args.input_dir,args.output_dir,num_processes = args.num_processes, orig_texts_dir=args.orig_texts_dir)
