import json
import boto3
import smart_open
import gzip

import multiprocessing as mp

import argparse 

def convert_file(obj: str, write_dir: str):
    okey = obj["Key"]
    filename = okey.split("/")[-1]
    with smart_open.open(f"s3://{bucket}/{okey}") as f:
        ct = 0
        toks_total = 0
        for line in f:
            ct += 1
            # d = json.loads(line)
            # toks = d["attributes"]["taggersec2__dolma_v2_tokenizer__length"][0][2]
            # toks_total += toks
        source = line.split(",")[3]
    cts = 0
    with smart_open.open(source) as f:
        cts = 0
        for line in f:
            cts += 1
    if ct != cts:
        print(f"BAD {okey} ---- {ct} ; {cts}")
    else:
        print(f"{okey} ---- {ct} ; {cts}")
    return ct,toks_total

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("subdir",type=str)
    parser.add_argument("num_processes",type=int)
    args = parser.parse_args()

    subdir = args.subdir
    num_processes = args.num_processes
    client = boto3.client('s3')

    bucket = "ai2-llm"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/source-added/tokens-dd/{subdir}"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
    write_dir = f"/home/ec2-user/source-added/{subdir}"
    # for page in pages:
    #     for obj in page["Contents"]:
    #         print(obj["Key"])
    results = []
    with mp.Pool(processes=num_processes) as pool:
        i = 0
        for page in pages:
            for obj in page["Contents"]:
                # i += 1
                # if i > 1: break
                if ".gz" not in obj["Key"]: continue
                result = pool.apply_async(convert_file, (obj,write_dir))
                results.append(result)
        docsum = 0
        toksum = 0
        with open(f"{subdir}_tokenized_doccount.txt","w") as out:
            for result in results:
                docs,toks = result.get()
                docsum += docs
                toksum += toks
                out.write(f"d = {docs}  ; t = {toks}\n")
            out.write(f"\n\n%%%%%%%%%%%%%\ndocs: {docsum}\n----\ntoks: {toksum}\n%%%%%%%%%%%%%")

        pool.close()
        pool.join()
