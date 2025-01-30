import os
import json
import smart_open
import re
import math
from collections import defaultdict

import multiprocessing as mp
import argparse

from prompt_templates import *

import random

from pathlib import Path

from transformers import GPT2Tokenizer


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

def yield_text_from_csv(args,csvfile):
    files_dict = defaultdict(set)
    with smart_open.open(csvfile) as f:
        for line in f:
            _, _, idx, docname, _ = line.strip().split(",")
            files_dict[docname].add(idx)
    for source_doc in files_dict:
        print(source_doc)
        print(len(files_dict[source_doc]))
        if args.needs_doc_insertion:
            dirname,fname = os.path.split(source_doc)
            doc_to_open = os.path.join(dirname,"documents",fname)
        else:
            doc_to_open = source_doc
        with smart_open.open(doc_to_open) as f:
            for line in f:
                d = json.loads(line.strip())
                if d["id"] in files_dict[source_doc]:
                    text = d["text"]
                    num_words = len(text.split())
                    if num_words > 500:
                        for i in range(math.ceil(num_words/500)):
                            yield text,d["id"]
                    else:
                        yield text,d["id"]

def convert_text_to_prompts(args,csvfile):
    distribution = [
        (OPEN_ENDED,.17),
        (STATEMENT_COMPLETION,.17),
        (FILL_IN_BLANK,.17),
        (TWO_STATEMENT,.05),
        (WHICH_HAS_PROPERTY,.17),
        (WHICH_TRUE,.17),
        (IN_QUESTION_OPTIONS,.1)
    ]
    values,probs = zip(*distribution)

    basename = csvfile.split("/")[-1].replace(".csv.gz","")
    
    total_size_mb = 0
    file_index = 0
    current_file_path = os.path.join(args.outdir,f"{basename}_f{file_index}.jsonl")
    current_file = open(current_file_path, "w")

    model = "gpt-4o-mini"
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

    i = 0
    num_written_requests = 0
    if model == "gpt-4o": 
        extra = " If the text doesn't contain any information relevant for an academic question, make academic questions inspired by words, phrases, or themes in the text."
    else:
        extra = ""
    for text,prompt_id in yield_text_from_csv(args,csvfile):
        # if i%10000 == 0: 
        #     print(i)
        random.seed(42)
        template = random.choices(values,weights = probs, k=1)[0]
        prompt = template.format(text=text,extra=extra)
        text_len = len(tokenizer.tokenize(text))
        max_tokens = round(max(text_len+(.1*text_len),150))
        # max_tokens = 100
        output_dict = {
            "custom_id": f"{basename}_{i}_{prompt_id}",
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
        i += 1
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
            current_file_path = os.path.join(args.outdir,f"{basename}_f{file_index}.jsonl")
            current_file = open(current_file_path, "w")
            # print(f"Started writing to new file: {current_file_path}")
            current_file.write(json_string)
            total_size_mb = size_in_mb
            num_written_requests = 1
    # print(total_size_mb)
    # print(num_written_requests)
    current_file.close()



def pull_items_parallel(args,csvfile_list):
    results = []
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    with mp.Pool(processes=args.num_processes) as pool:
        for csvfile in csvfile_list:
            result = pool.apply_async(convert_text_to_prompts, (args,csvfile))
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
    parser.add_argument("--needs_doc_insertion",action="store_true")
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()
    csv_list = get_doc_list_from_tokenized(args.config,args.tokfilepattern)
    
    # print(csv_list[0])
    # tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    # Path(args.outdir).mkdir(parents=True, exist_ok=True)
    # convert_text_to_prompts(args,csv_list[0])
   
    pull_items_parallel(args,csv_list)
