import json
import boto3
import smart_open
import gzip
import os

from collections import Counter

import multiprocessing as mp

import argparse 

def convert_file(obj: str):
    okey = obj["Key"]
    filename = okey.split("/")[-1]
    with smart_open.open(f"s3://{bucket}/{okey}") as f:
        subreddit_doc_counter = Counter()
        subreddit_tok_counter = Counter()
        print(okey)
        for line in f:
            d = json.loads(line)
            sub = d["metadata"]["subreddit"]
            subreddit_doc_counter[sub] += 1
            toks = d["attributes"]["taggersec2__dolma_v2_tokenizer__length"][0][2]
            subreddit_tok_counter[sub] += toks
        # print(f"{okey} ---- {ct}")
    return subreddit_doc_counter,subreddit_tok_counter,okey

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("subdir",type=str)
    parser.add_argument("num_processes",type=int)
    args = parser.parse_args()

    subdir = args.subdir
    num_processes = args.num_processes
    client = boto3.client('s3')

    bucket = "ai2-llm"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa/mixed/{subdir}/"
    # filedir = f"pretraining-data/sources/reddit/dolma_raw/source-added/mixed-dd/{subdir}/"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=f"{filedir}")

    results = []
    with mp.Pool(processes=num_processes) as pool:
        for page in pages:
            for obj in page["Contents"]:
                if ".gz" not in obj["Key"]: continue
                result = pool.apply_async(convert_file, (obj,))
                results.append(result)
        tot_doc_counter = Counter()
        tot_tok_counter = Counter()
        with open(f"output_count_files/subreddit_counts/{subdir}_subredditcount.txt","w") as out:
            for result in results:
                doc_counter,tok_counter,fname = result.get()
                tot_doc_counter.update(doc_counter)
                tot_tok_counter.update(tok_counter)
                out.write(fname + "\n")
            for subreddit,_ in sorted(tot_doc_counter.items(),key=lambda x:x[1],reverse=True):
                out.write(f"{subreddit}: d = {tot_doc_counter[subreddit]}  ; t = {tot_tok_counter[subreddit]}\n")

        pool.close()
        pool.join()
