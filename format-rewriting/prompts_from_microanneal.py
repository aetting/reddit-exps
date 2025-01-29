import os
import json
import smart_open
import re
import math
from collections import defaultdict

import multiprocessing as mp
import argparse

import random

from pathlib import Path

from transformers import GPT2Tokenizer

from format_rewriting_core import text_to_prompt, write_batch_files


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


def write_batch_files_from_tokenizer_csvfile(args,csvfile):
    text_iterator = yield_text_from_csv(args,csvfile)
    batch_files_basename = csvfile.split("/")[-1].replace(".csv.gz","")
    tokenizer_for_length_estimates = GPT2Tokenizer.from_pretrained("gpt2")
    write_batch_files(text_iterator,batch_files_basename,args.model,args.outdir,tokenizer_for_length_estimates)

def pull_items_parallel(args,csvfile_list):
    results = []
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    with mp.Pool(processes=args.num_processes) as pool:
        for csvfile in csvfile_list:
            result = pool.apply_async(write_batch_files_from_tokenizer_csvfile, (args,csvfile))
            results.append(result)

        pool.close()
        pool.join()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",type=int)
    parser.add_argument("--model",type=str,default="gpt-4o-mini")
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
    # write_batch_files_from_tokenizer_csvfile(args,csv_list[0])
   
    pull_items_parallel(args,csv_list)
