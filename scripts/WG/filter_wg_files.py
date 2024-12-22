import json
import boto3
import smart_open
import gzip

import multiprocessing as mp

import argparse 
import re
import math

def convert_file(obj: str):
    # print(obj)
    filename = obj.split("/")[-1]
    # print(filename)
    with smart_open.open(obj) as f,gzip.open(f"/home/ec2-user/wg-filtered-new2/{filename}","wt") as out:
        tot = 0
        skipped = 0
        # print(filename)
        for line in f:
            tot += 1
            d = json.loads(line)
            output = d["outputs"][0]["text"]
            # if i == 1:
            #     print(f"{filename}: {d['text']}")
            label = re.match("Harmful request: (.*)\nResponse refusal:",output).groups()[0]
            if label == "yes":
                out.write(json.dumps(d) + "\n")
                skipped += 1
        out.write(f"skipped {skipped} out of {tot} ({skipped/tot}) in {filename}")

    # client.put_object(Body=open(f"/home/ec2-user/wg-filtered-new2/{filename}", 'rb'), Bucket="ai2-llm", Key=f"")

    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("num_processes",type=int)
    args = parser.parse_args()

    num_processes = args.num_processes
    client = boto3.client('s3')


    files_list = []
    bucket = "ai2-llm"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/wildguard_tagging/tagged_full_new2/"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
    for page in pages:
        # import pdb; pdb.set_trace()
        for obj in page["Contents"]:
            okey = obj["Key"]
            if ".gz" not in okey: continue
            files_list.append(f"s3://{bucket}/{okey}")

    results = []
    with mp.Pool(processes=num_processes) as pool:
        i = 0
        for obj in files_list:
            # i += 1
            # if i > 1: break
            # if ".gz" not in obj["Key"]: continue
            result = pool.apply_async(convert_file, (obj,))
            results.append(result)
        # full_tok_list = []
        # # with open(f"{subdir}_tokenized_doccount.txt","w") as out:
        # tok_total = 0
        # for result in results:
        #     toks,fname = result.get()
        #     tok_total += toks
        #     full_tok_list.append((toks,fname))
        # print(tok_total)

        pool.close()
        pool.join()
    

