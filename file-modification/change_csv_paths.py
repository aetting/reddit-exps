import json
import boto3
import smart_open
import gzip
import csv

import multiprocessing as mp

import argparse 
import re
import math
import pathlib
import os

"""
open csv file
for each line, pull out the original file
extract the basename to lookup in manifest
/mnt/raid0/ai2-llm/pretraining-data/sources/wiki_psgqa_rewrites/psgqa_rewrites_v1-decon-sparkle-motion/00044_f348.jsonl.gz
""" 

def convert_file(filepath,bin_lookup,outdir):
    # okey = obj["Key"]
    filename = filepath.split("/")[-1]
    # with smart_open.open(f"s3://{bucket}/{okey}",'rt', encoding='utf-8') as f_in, \
    #     gzip.open(f"{outdir}/{filename}", 'wt', encoding='utf-8', newline='') as f_out:
    
    with gzip.open(filepath, 'rt', encoding='utf-8') as f_in, \
        gzip.open(f"{outdir}/{filename}", 'wt', encoding='utf-8', newline='') as f_out:
        
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        
        for row in reader:
            # Check if row has at least 4 columns (index 3)
            if len(row) > 3:
                # Substitute string in column 4 (index 3)
                m = re.match("/mnt/raid0/ai2-llm/pretraining-data/sources/wiki_psgqa_rewrites/psgqa_rewrites_v1-decon-sparkle-motion/(.*).gz",row[3]) 
                source_basename = m.groups()[0]
                binname = bin_lookup[source_basename]
                # old_string = "/mnt/raid0/ai2-llm/pretraining-data/sources/wiki_psgqa_rewrites/psgqa_rewrites_v1-decon-sparkle-motion/"
                new_string = f"wiki_to_rcqa-{binname}"
                # row[3] = row[3].replace(old_string, new_string).replace(".gz",".zst")
                row[3] = f"{new_string}/{source_basename}.zst"
            
            writer.writerow(row)

def process_manifest(csvfilename):
    bin_lookup = {}
    with open(csvfilename) as csvf:
        reader = csv.reader(csvf)
        for row in reader:
            binname,fname,_ = row 
            fname = fname.replace(".zst","")
            bin_lookup[fname] = binname
    return bin_lookup 


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",default=mp.cpu_count(),type=int)
    parser.add_argument("--s3_subdir",type=str,default=None)
    parser.add_argument("--manifest",type=str,default=None)
    parser.add_argument("--outdir",type=str,default=None)
    parser.add_argument("--indir",type=str,default=None)
    args = parser.parse_args()

    num_processes = args.num_processes
    client = boto3.client('s3')

    files_list = [f"{args.indir}/{e}" for e in os.listdir(args.indir) if "csv.gz" in e]
    # bucket = "ai2-llm"
    # filedir = args.s3_subdir
    # paginator = client.get_paginator('list_objects_v2')
    # pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
    # for page in pages:
    #     for obj in page["Contents"]:
    #         okey = obj["Key"]
    #         if "csv.gz" not in okey: continue
    #         files_list.append(f"s3://{bucket}/{okey}")

    results = []

    # outdir = "/mnt/raid0"
    # for folder in [
    #     "wiki_to_rcqa-part1",
    #     "wiki_to_rcqa-part2",
    #     "wiki_to_rcqa-part3"]:
    #     pathlib.Path(f'{outdir}/{folder}').mkdir(parents=True, exist_ok=True)

    outdir = args.outdir

    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    
    bin_lookup = process_manifest(args.manifest)
    convert_file(files_list[0],bin_lookup,outdir)
    import pdb; pdb.set_trace()
    
    with mp.Pool(processes=num_processes) as pool:
        for filepath in files_list:
            result = pool.apply_async(convert_file, (filepath,bin_lookup,outdir))
            results.append(result)
        for result in results:
            result.get()

        pool.close()
        pool.join()