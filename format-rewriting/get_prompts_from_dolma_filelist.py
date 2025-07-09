import json
import smart_open
import argparse
import math
import boto3

from pathlib import Path
import multiprocessing as mp

from transformers import GPT2Tokenizer

from format_rewriting_core import text_to_prompt, write_batch_files

#for converting to openai batch files, need to define an iterator that yields the raw text to be converted to prompts, and text id
def yield_text_from_dolma_jsonl(filename):
    print(f"Processing {filename}")
    with smart_open.open(filename) as f:
        for line in f:
            d = json.loads(line.strip())
            text = d["text"]
            num_words = len(text.split())
            if num_words > 500:
                for i in range(math.ceil(num_words/500)):
                    yield text,d["id"]
            else:
                yield text,d["id"]

def convert_file_to_batch_files(filename,args):
    text_iterator = yield_text_from_dolma_jsonl(filename)
    
    batch_files_basename = filename.split("/")[-1].replace(".json.gz","")
    tokenizer_for_length_estimates = GPT2Tokenizer.from_pretrained("gpt2")
    
    write_batch_files(text_iterator,batch_files_basename,args.model,args.outdir,tokenizer_for_length_estimates)

def list_s3_files(input_file_folder):
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
            if ".json" not in okey:
                continue
            filenames.append(s3_prefix + okey)
    return filenames

def process_files_parallel(args,file_list):
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    with mp.Pool(processes=args.num_processes) as pool:
        for filename in file_list:
            pool.apply_async(convert_file_to_batch_files, (filename,args))

        pool.close()
        pool.join()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",type=int)
    parser.add_argument("--model",type=str,default="gpt-4o-mini")
    parser.add_argument("--input_dir",type=str,default=None)
    parser.add_argument("--outdir",type=str,default=None)

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    
    #example file_list
    # file_list = [
    #     "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_lowthresh/documents/merged_qa_prefilter_densesubs_lowthresh-0000.json.gz",
    #     "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_lowthresh/documents/merged_qa_prefilter_densesubs_lowthresh-0001.json.gz",
    #     "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_lowthresh/documents/merged_qa_prefilter_densesubs_lowthresh-0002.json.gz",
    #     "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_lowthresh/documents/merged_qa_prefilter_densesubs_lowthresh-0003.json.gz",
    #     "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_lowthresh/documents/merged_qa_prefilter_densesubs_lowthresh-0004.json.gz",
    # ]

    args = parse_args()

    file_list = list_s3_files(args.input_dir)
    print(file_list)
    print(len(file_list))

    # convert_file_to_batch_files(file_list[0],args)

    process_files_parallel(args,file_list)
