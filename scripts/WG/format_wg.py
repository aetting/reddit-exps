import json
import boto3
import smart_open
import gzip
import csv
import re

import multiprocessing as mp

import argparse 

def convert_file(obj: str):
    okey = obj["Key"]
    filename = okey.split("/")[-1]
    print(filename)
    this_results = []
    with smart_open.open(f"s3://{bucket}/{okey}") as f:
        i = 0
        for line in f:
            i += 1
            if i > 1000: break
            d = json.loads(line)
            t = d["text"]
            o = d["outputs"][0]["text"]
            m = re.match("Harmful request: (.*)\nResponse refusal.*",o)
            label = m.groups()[0].upper()
            this_results.append({"Text":t,"Harmful": label})
    return this_results


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("num_processes",type=int)
    args = parser.parse_args()

    num_processes = args.num_processes
    client = boto3.client('s3')

    bucket = "ai2-llm"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/wildguard_tagging/tagged_sample/raw"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=f"{filedir}")

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
                result = pool.apply_async(convert_file, (obj,))
                results.append(result)
        with open('wg_sample.csv', 'w', newline='') as csvfile:
            # writer = csv.writer(csvfile,delimiter=',',quotechar='|', quoting=csv.QUOTE_ALL,lineterminator='\n')
            writer = csv.DictWriter(csvfile,fieldnames=["Text","Harmful"],quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            # writer.writerow(["Text","Harmful request"])
            for result in results:
                for row in result.get():
                    writer.writerow(row)

        pool.close()
        pool.join()
