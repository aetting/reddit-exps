import json
import boto3
import smart_open
import gzip

import multiprocessing as mp

import argparse 

def convert_file(obj: str, write_dir: str):
    okey = obj["Key"]
    filename = okey.split("/")[-1]
    with smart_open.open(f"s3://{bucket}/{okey}") as f,gzip.open(f"{write_dir}/{filename}","wt") as out:
        for line in f:
            d = json.loads(line)
            # print(d)
            d["source"] = "reddit"
            out.write(json.dumps(d) + "\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("subdir",type=str)
    parser.add_argument("num_processes",type=int)
    args = parser.parse_args()

    subdir = args.subdir
    num_processes = args.num_processes
    client = boto3.client('s3')

    bucket = "ai2-llm"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/documents/{subdir}"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=f"{filedir}/raw")

    write_dir = f"/home/ec2-user/source-added/{subdir}"
    # for page in pages:
    #     for obj in page["Contents"]:
    #         print(obj["Key"])
    results = []
    with mp.Pool(processes=num_processes) as pool:
        for page in pages:
            for obj in page["Contents"]:
                result = pool.apply_async(convert_file, (obj,write_dir))
                results.append(result)
        for result in results:
            result.get()

        pool.close()
        pool.join()
