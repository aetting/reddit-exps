import json
import os
import re
import gzip
import random
import argparse

import smart_open
import boto3

import multiprocessing as mp


def iterate_over_files(input_file_folder,output_dir, num_processes=1):
    os.makedirs(output_dir,exist_ok=True)

    if "s3://" in input_file_folder:
        client = boto3.client('s3')
        bucket = "ai2-llm"
        s3_prefix = "s3://" + bucket + "/"
        filedir = input_file_folder.replace(s3_prefix,"")
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
        filenames = []
        for page in pages:
            for obj in page["Contents"]:
                okey = obj["Key"]
                if ".jsonl" not in okey:
                    continue
                filenames.append(s3_prefix + okey)
    else:
        filenames = [os.path.join(input_file_folder,f) for f in os.listdir(input_file_folder) if ".jsonl" in f]
    
    with mp.Pool(processes=num_processes) as pool:
        for filename in filenames:
            pool.apply_async(convert_file_to_dolma, (filename,output_dir))
        pool.close()
        pool.join()


def convert_file_to_dolma(input_filename,outputdir):

    basename = os.path.basename(input_filename)
    print(f"Processing {input_filename}")
    
    with smart_open.open(os.path.join(input_filename)) as f, gzip.open(os.path.join(outputdir,basename+".gz"),"wt") as out:
        for line in f:
            d = json.loads(line.strip())
            idx = d["custom_id"]
            response_text = d["response"]["body"]["choices"][0]["message"]["content"]
            parsed_text = response_text.split("%%%%")
            for i,q_text in enumerate(parsed_text):
                if not re.match(".*Answer:",q_text,re.DOTALL):
                    continue
                add_q = random.choices([0,1])[0]
                text = q_text.strip()
                if add_q:
                    text = "Question: " + text
                qid = f"{idx}_{i}"
                out_object = {
                    "id":qid,
                    "text":text 
                }
                out.write(json.dumps(out_object) + "\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",type=int)
    parser.add_argument("--input_dir",type=str)
    parser.add_argument("--output_dir",type=str)
    args = parser.parse_args()

    iterate_over_files(args.input_dir,args.output_dir,num_processes = args.num_processes)
