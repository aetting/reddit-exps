import os
import json
import smart_open
import re
from collections import defaultdict

import multiprocessing as mp
import argparse

from prompt_templates import *

import random

from pathlib import Path


def return_json_objs_from_s3_files(filename_list):
    for filename in filename_list:
        with smart_open.open(filename) as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    yield json.loads(line)

def read_jsonl_from_s3(file_keys):
    """
    Reads JSONL files from S3 and returns each line as a Python dictionary.

    :param bucket_name: Name of the S3 bucket.
    :param file_keys: List of S3 keys (filenames) to process.
    :return: Generator yielding each line as a dictionary.
    """
    # s3 = boto3.client('s3')
    
    for file_key in file_keys:
        print(f"Processing file: {file_key}")
        # response = s3.get_object(Bucket=bucket_name, Key=file_key)
        # content = response['Body'].read().decode('utf-8')
        with smart_open.open(file_key) as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    yield json.loads(line)

def get_doc_list_from_tokenized(config,strmatch):
    doclist = []
    pattern = r".*(s3://.*" + re.escape(strmatch) + r".*)\.npy"
    with open(config) as f:
        for line in f:
            m = re.match(pattern,line)
            if m:
                csvfile = m.groups()[0] + ".csv.gz"
                doclist.append(csvfile)
    return(doclist)

def yield_text_from_csv(csvfile):
    files_dict = defaultdict(set)
    with smart_open.open(csvfile) as f:
        for line in f:
            _, _, idx, docname, _ = line.strip().split(",")
            files_dict[docname].add(idx)
    for source_doc in files_dict:
        print(source_doc)
        with smart_open.open(source_doc) as f:
            for line in f:
                d = json.loads(line.strip())
                if d["id"] in files_dict[source_doc]:
                    yield d["text"]

def convert_text_to_prompts(args,csvfile):
    distribution = [
        (OPEN_ENDED,.19)
        (STATEMENT_COMPLETION,.19)
        (FILL_IN_BLANK,.19)
        (TWO_STATEMENT,.05)
        (WHICH_HAS_PROPERTY,.19)
        (WHICH_TRUE,.19)
    ]
    values,probs = zip(*distribution)

    basename = csvfile.split("/")[-1].replace(".csv.gz",".jsonl")
    
    with open(os.path.join(args.outdir,basename),"w") as out:
        for text in yield_text_from_csv(csvfile):
            template = random.choices(values,weights = probs, k=1)
            prompt = template.format(text=text)
            out.write(json.dumps({"prompt":prompt}) + "\n")


def pull_items_parallel(args,csvfile_list):
    results = []
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    with mp.Pool(processes=args.num_processes) as pool:
        for csvfile in csvfile_list[:5]:
            result = pool.apply_async(convert_text_to_prompts, (csvfile,))
            results.append(result)
        # for result in results:
        #     toks,fname = result.get()
        #     tok_total += toks
        #     full_tok_list.append((toks,fname))
        # print(tok_total)

        pool.close()
        pool.join()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",type=int)
    parser.add_argument("--config",type=str,default=None)
    parser.add_argument("--tokfilepattern",type=str,default=None)
    parser.add_argument("--outdir",type=str,default=None)
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()
    csv_list = get_doc_list_from_tokenized(args.config,args.tokfilepattern)
    print(csv_list)
