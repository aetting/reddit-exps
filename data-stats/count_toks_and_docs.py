import json
import boto3
import smart_open
import gzip

import multiprocessing as mp

import argparse 
import re
import math

def convert_file(obj: str):
    print(obj)
    with smart_open.open(obj) as f:
        ct = 0
        toks_total = 0
        for line in f:
            ct += 1
        last_line = line
        file_total = int(last_line.split(",")[1])
    
    return (file_total,ct,obj) 

def process_list(listfile):
    files_list = []
    with open(listfile) as f:
        for line in f:
            m = re.match(".*(s3://.*)\.npy.*",line,re.DOTALL)
            if m:
                files_list.append(m.groups()[0] + ".csv.gz")

    return files_list


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",default=mp.cpu_count(),type=int)
    parser.add_argument("--s3_subdir",type=str,default=None)
    parser.add_argument("--from_config",type=str,default=None)
    args = parser.parse_args()

    num_processes = args.num_processes
    client = boto3.client('s3')

    if args.from_config:
        files_list = process_list(args.from_config)
    elif args.s3_subdir:
        files_list = []
        bucket = "ai2-llm"
        filedir = args.s3_subdir
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
        for page in pages:
            for obj in page["Contents"]:
                okey = obj["Key"]
                if "csv.gz" not in okey: continue
                files_list.append(f"s3://{bucket}/{okey}")

    results = []
    with mp.Pool(processes=num_processes) as pool:
        i = 0
        for obj in files_list:
            result = pool.apply_async(convert_file, (obj,))
            results.append(result)
        full_tok_list = []
        tok_total = 0
        doc_total = 0
        for result in results:
            toks,docs,fname = result.get()
            tok_total += toks
            doc_total += docs
            full_tok_list.append((toks,fname))
        print(f"TOKS: {tok_total}")
        print(f"DOCS: {doc_total}")

        pool.close()
        pool.join()