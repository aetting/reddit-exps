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
            pass
        last_line = line
        file_total = int(last_line.split(",")[1])
    
    return (file_total,obj) 

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
    parser.add_argument("num_processes",type=int)
    parser.add_argument("--from_config",type=str,default=None)
    parser.add_argument("--s3_subdir",type=str,default=None)
    parser.add_argument("--counts_only",action='store_true')
    args = parser.parse_args()

    num_processes = args.num_processes
    client = boto3.client('s3')

    if args.from_config:
        files_list = process_list(args.from_config)
    elif args.s3_subdir:
        files_list = []
        bucket = "ai2-llm"
        filedir = {args.s3_subdir}
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
        for page in pages:
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
        full_tok_list = []
        # with open(f"{subdir}_tokenized_doccount.txt","w") as out:
        tok_total = 0
        for result in results:
            toks,fname = result.get()
            tok_total += toks
            full_tok_list.append((toks,fname))
        print(tok_total)

        pool.close()
        pool.join()

    if not args.counts_only:
        running_sum = 0
        files_to_keep = []
        target = 17969522512
        for i,(val,f) in enumerate(full_tok_list):
            if running_sum + val <= target:
                running_sum += val
                files_to_keep.append((val,f))
                used = i
            else: 
                break
        
        #remove final addition and keep it as a candidate
        running_sum -= full_tok_list[used][0]
        files_to_keep.pop()

        min_diff = math.inf
        ftl_sort = sorted(full_tok_list[used:],key = lambda x: x[0])
        for v,f in ftl_sort:
            if ((running_sum + v) - target) < abs(min_diff):
                cand = (v,f)
                min_diff = ((running_sum + v) - target)
            elif (running_sum + v) > target:
                break
        files_to_keep.append(cand)
        print(sum([x[0] for x in files_to_keep]))

        #write selected files to output file
        name = args.from_config.split("/")[-1].replace(".txt","") if args.from_config else args.s3_subdir
        with open(f"output_count_files/selected_files-{name}-{target}.txt","w") as out:
            final_sum = 0
            for v,f in files_to_keep:
                final_sum += v
                out.write(f"- {f.replace('.csv.gz','.npy')}\n")
    

