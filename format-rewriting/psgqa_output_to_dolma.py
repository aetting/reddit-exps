import json
import os
import re
import gzip
import random
import argparse

import smart_open
import boto3

import multiprocessing as mp


def get_filelist(input_file_folder):

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

    return filenames

def get_passages(input_filename):
    psg_dict = {}
    with smart_open.open(input_filename) as fpsg:
        for line in fpsg:
            d = json.loads(line)
            idx = d["custom_id"]
            prompt = d["body"]["messages"][1]["content"]
            m = re.match('.*Here is the passage:\n\n\"(.*)\"\n\nGenerate [0-9] question',prompt, re.DOTALL)
            # import pdb; pdb.set_trace()
            text = m.groups()[0]
            psg_dict[idx] = text
    return psg_dict
            

def iterate_over_files(filelist,psg_input_dir, output_dir, num_processes=1):
    with mp.Pool(processes=num_processes) as pool:
        for filename in filelist:
            pool.apply_async(convert_file_to_dolma, (filename,psg_input_dir,output_dir))
        pool.close()
        pool.join()

def convert_file_to_dolma(input_filename,psg_input_dir,outputdir):

    # basename = os.path.basename(input_filename)
    print(f"Processing {input_filename}")
    
    orig_file_name = input_filename.split("format_rewriting_batches1_")[1]

    psg_dict = get_passages(os.path.join(psg_input_dir,orig_file_name))
    
    random.seed(42)
    with smart_open.open(input_filename) as fgen, gzip.open(os.path.join(outputdir,orig_file_name+".gz"),"wt") as out:
        for line in fgen:
            d = json.loads(line.strip())
            idx = d["custom_id"]
            response_text = d["response"]["body"]["choices"][0]["message"]["content"]
            psg = psg_dict[idx]
            # import pdb; pdb.set_trace()
            # parsed_text = response_text.split("%%%%")
            # for i,q_text in enumerate(parsed_text):
            #     if not re.match(".*Answer:",q_text,re.DOTALL):
            #         continue
            #     # add_q = random.choices([0,1])[0]
            #     text = q_text.strip()
            #     # if add_q:
            #     #     text = "Question: " + text
            #    qid = f"{idx}_{i}"
            full_text = f"Passage: {psg}\n\n{response_text}"
            # print(full_text)
            # print("\n\n%%%%\n\n")

            out_object = {
                "id":idx,
                "text":full_text 
            }
            out.write(json.dumps(out_object) + "\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",type=int,default=1)
    parser.add_argument("--gen_input_dir",type=str)
    parser.add_argument("--psg_input_dir",type=str)
    parser.add_argument("--output_dir",type=str)
    args = parser.parse_args()

    os.makedirs(args.output_dir,exist_ok=True)

    psg_input_dir = "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/format_rewriting/wiki_psgqa_batches1/"
    gen_input_dir = "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/format_rewriting/wiki_psgqa_batches1_generations/"

    gen_filelist = get_filelist(gen_input_dir)
    # psg_filelist = get_filelist(psg_input_dir)
    # print(psg_filelist[0])

    # convert_file_to_dolma(gen_filelist[0],psg_input_dir,args.output_dir)
    iterate_over_files(gen_filelist,psg_input_dir,args.output_dir,num_processes = args.num_processes)
