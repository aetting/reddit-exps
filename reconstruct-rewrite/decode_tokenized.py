import os
import click
from dolma.core.paths import cached_path
import numpy as np
from transformers import AutoTokenizer

import json
import boto3
import smart_open
import gzip

import multiprocessing as mp

import argparse 

import re

import csv


# @click.command()
# @click.argument("tokenized_file")
# @click.option("--tokenizer-name-or-path", default="allenai/gpt-neox-olmo-dolma-v1_5")
# @click.option("--chunk-size", default=1024**2, type=int)

def cross_reference(okey, tokenizer_name_or_path="allenai/dolma2-tokenizer"):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path)

    bucket = "ai2-llm"
    tokenized_file = f"s3://{bucket}/{okey}"
    metadata_file = tokenized_file.replace(".npy",".csv.gz")

    get_metadata(metadata_file)

    path = cached_path(tokenized_file)
    size = os.path.getsize(path)
    data = np.memmap(path, dtype='uint16', mode='r', shape=(size // 2,))

    # print(data[:600])
    # print(len(data))

    qid = 14924
    eos_id = 34721

    i = 0
    for start_loc,end_loc,item_id,file_out,_ in get_metadata(metadata_file):
        toks = data[int(start_loc)+1:int(end_loc)]
        output = tokenizer.decode(toks)
        print(toks)
        print(output)

        i += 1
        if i > 10: break

    # collection = []
    # i = 0
    # for e in data:
    #     if e == eos_id:
    #         # output = tokenizer.decode(collection)
    #         start = collection[:2]
    #         # print(collection)
            
    #         v1 = start == [qid,25]
    #         # v2 = output.startswith('Question:')
    #         # if v1 != v2:
    #         #     print(collection)
    #         #     print(output[:20])
    #         #     print(f"{v1} --- {v2}")
    #         #     print()
    #         collection = []
    #         i += 1
    #         if i%1000 == 0:
    #             print(i)
    #         # if i > 100:
    #         #     break
    #     else:
    #         if e not in [0,1]:
    #             collection.append(e)
        # chunk = data[i : i + chunk_size]
        # i += chunk_size

        # while (chunk == 34721).any():
        #     print("here")
        #     # split chunk into before and after eos
        #     eos_idx = np.where(chunk == 34721)[0][0] + 1
        #     collection.extend(chunk[:eos_idx].tolist())
        #     output = tokenizer.decode(collection)
        #     print('#' * os.get_terminal_size().columns)
        #     print(output)
        #     input("#" * os.get_terminal_size().columns)
        #     # reset collection
        #     collection = []
        #     chunk = chunk[eos_idx:]

        # collection.extend(chunk.tolist())

def get_metadata(filepath):
    with smart_open.open(filepath, 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            yield row
    

if __name__ == "__main__":
    # inspect_tokenized("allenai/dolma2-tokenizer")
    parser = argparse.ArgumentParser()
    parser.add_argument("num_processes",type=int)
    args = parser.parse_args()

    num_processes = args.num_processes
    client = boto3.client('s3')

    bucket = "ai2-llm"
    # filedir = f"pretraining-data/sources/reddit/dolma_raw/format_rewriting/densesub_highthresh_microanneal_4omini_rewrite_tokenized/"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/format_rewriting/tokenized_mini/"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
    # for page in pages:
    #     for obj in page["Contents"]:
    #         print(obj["Key"])
    results = []

    # print(pages[0][0])

    # get_doc_list_from_tokenized()

    with mp.Pool(processes=num_processes) as pool:
        i = 0
        for page in pages:
            for obj in page["Contents"]:
                okey = obj["Key"]
                if ".npy" not in obj["Key"]: continue
                print(okey)
                cross_reference(okey)
                # i += 1
                # if i > 2: break
                # result = pool.apply_async(get_doc_list_from_tokenized, (okey,))
                # results.append(result)
        # docsum = 0
        # toksum = 0
        # with open(f"{subdir}_tokenized_doccount.txt","w") as out:
        # s = set()
        # for result in results:
        #     docslist = result.get()
        #     s = s.union(docslist)
        #         out.write(f"d = {docs}  ; t = {toks}\n")
        #     out.write(f"\n\n%%%%%%%%%%%%%\ndocs: {docsum}\n----\ntoks: {toksum}\n%%%%%%%%%%%%%")

        # print(s)
        # print(len(s))
        pool.close()
        pool.join()
