import json
import boto3
import smart_open
import gzip
import os

import multiprocessing as mp

import argparse 

def convert_file(obj: str):
    okey = obj["Key"]
    filename = okey.split("/")[-1]
    with smart_open.open(f"s3://{bucket}/{okey}") as f:
    # with smart_open.open(obj) as f:
        ct = 0
        toks_total = 0
        print(okey)
        for line in f:
            ct += 1
            d = json.loads(line)
            # toks = d["attributes"]["taggersec2__dolma_v2_tokenizer__length"][0][2]
            toks = d["attributes"]["prelim_filters__dolma_v2_tokenizer__length"][0][2]
            toks_total += toks
        # print(f"{okey} ---- {ct}")
    return ct,toks_total,okey

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("subdir",type=str)
    parser.add_argument("num_processes",type=int)
    args = parser.parse_args()

    subdir = args.subdir
    num_processes = args.num_processes
    client = boto3.client('s3')

    bucket = "ai2-llm"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_all_wsubreddit/{subdir}/"
    # filedir = f"pretraining-data/sources/reddit/dolma_raw/source-added/mixed-dd/{subdir}/"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=filedir)

    results = []
    with mp.Pool(processes=num_processes) as pool:
        i = 0
        # for x in [1]:
        #     for fname in os.listdir("/home/ec2-user/wg-filtered-new2"):
        #         obj = f"/home/ec2-user/wg-filtered-new2/{fname}"

        for page in pages:
            for obj in page["Contents"]:
                if ".gz" not in obj["Key"]: continue
                result = pool.apply_async(convert_file, (obj,))
                results.append(result)
        docsum = 0
        toksum = 0
        with open(f"output_count_files/{subdir}_doccount.txt","w") as out:
            for result in results:
                docs,toks,fname = result.get()
                docsum += docs
                toksum += toks
                out.write(f"d = {docs}  ; t = {toks} ; {fname}\n")
            out.write(f"\n\n%%%%%%%%%%%%%\ndocs: {docsum}\n----\ntoks: {toksum}\n%%%%%%%%%%%%%")

        pool.close()
        pool.join()
