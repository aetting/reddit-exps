import json
import boto3
import smart_open
import gzip

import multiprocessing as mp

import argparse 

import re

def get_doc_list_from_tokenized(okey: str):
    # filename = okey.split("/")[-1]
    print(okey)
    bucket = "ai2-llm"
    with smart_open.open(f"s3://{bucket}/{okey}") as f:
        doclist = set()
        pattern = ".*(/home.*)\.gz"
        for line in f:
            m = re.match(pattern,line)
            if m:
                csvfile = m.groups()[0] + ".csv.gz"
                doclist.add(csvfile)
    for e in doclist:
        print(e)
    return(doclist)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("num_processes",type=int)
    args = parser.parse_args()

    num_processes = args.num_processes
    client = boto3.client('s3')

    bucket = "ai2-llm"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/format_rewriting/densesub_highthresh_microanneal_4omini_rewrite_tokenized/"
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
                if ".gz" not in obj["Key"]: continue
                # print(okey)
                # i += 1
                # if i > 2: break
                result = pool.apply_async(get_doc_list_from_tokenized, (okey,))
                results.append(result)
        # docsum = 0
        # toksum = 0
        # with open(f"{subdir}_tokenized_doccount.txt","w") as out:
        s = set()
        for result in results:
            docslist = result.get()
            s = s.union(docslist)
        #         out.write(f"d = {docs}  ; t = {toks}\n")
        #     out.write(f"\n\n%%%%%%%%%%%%%\ndocs: {docsum}\n----\ntoks: {toksum}\n%%%%%%%%%%%%%")

        print(s)
        print(len(s))
        pool.close()
        pool.join()


