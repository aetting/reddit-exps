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

def decode_tokenized(okey, outputdir, tokenizer_name_or_path="allenai/dolma2-tokenizer"):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path)

    bucket = "ai2-llm"
    tokenized_file = f"s3://{bucket}/{okey}"
    metadata_file = tokenized_file.replace(".npy",".csv.gz")

    get_metadata(metadata_file)

    path = cached_path(tokenized_file)
    # size = os.path.getsize(path)
    data = np.memmap(path, dtype='uint32', mode='r')

    # print(data[:600])
    # print(len(data))

    qid = 14924
    colid = 25
    eos_id = 34721

    basefilename = os.path.basename(tokenized_file).replace(".npy","")

    output_full = os.path.join(outputdir,basefilename+"-decoded.jsonl")
    metapath = os.path.join(outputdir,basefilename+"-meta.json")

    source_files = []

    with open(output_full,"w") as out:
        i = 0
        for start_loc,end_loc,item_id,file_out,_ in get_metadata(metadata_file):
            if file_out not in source_files:
                source_files.append(file_out)
            if i > 100000: break
            # print(item_id)
            toks = data[int(start_loc):int(end_loc)-1]
            output = tokenizer.decode(toks)
            # v1 = toks[:2] == [qid,colid]
            out.write(json.dumps({"id":item_id,"text": output}) + "\n")
            # v2 = output.startswith("Question:")

            # if not v1 and output.startswith("Question"):
            #     print(f"%%%%%%%%")
            #     # print(toks)
            #     print(output)
            #     print(v1)
            #     print(v2)
            #     print("%%%%%%%%")
            # print(toks)
            # print(output)

            i += 1
            # if i%100000 == 0: print(i)
    with open(metapath,"w") as meta_file:
        json.dump(source_files,meta_file,indent=3)



def get_metadata(filepath):
    with smart_open.open(filepath, 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            yield row
    

if __name__ == "__main__":
    # inspect_tokenized("allenai/dolma2-tokenizer")
    parser = argparse.ArgumentParser()
    parser.add_argument("num_processes",type=int)
    parser.add_argument("outputdir",type=str)
    args = parser.parse_args()

    num_processes = args.num_processes
    outputdir = args.outputdir
    client = boto3.client('s3')

    os.makedirs(outputdir,exist_ok=True)

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
                # decode_tokenized(okey,outputdir)
                # i += 1
                # if i > 2: break
                result = pool.apply_async(decode_tokenized, (okey,outputdir))
                results.append(result)
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
