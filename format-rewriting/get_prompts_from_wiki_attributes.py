import json
import smart_open
import argparse
import math
import boto3

from pathlib import Path
import multiprocessing as mp

from transformers import GPT2Tokenizer

from passage_qa_rewriting_core import text_to_prompt, write_batch_files

#for converting to openai batch files, need to define an iterator that yields the raw text to be converted to prompts, and text id
def yield_text_from_wiki_attributes(filename):
    print(f"Processing {filename}")
    with smart_open.open(filename) as f:
        for line in f:
            d = json.loads(line.strip())
            if "wikiclean__wikiclean__summary" not in d["attributes"]:
                continue
            summary = d["attributes"]["wikiclean__wikiclean__summary"][0][2]
            text = d["attributes"]["wikiclean__wikiclean__full_text"][0][2]
            sections = text.split("\n\n")
            passages = [summary]
            for section in sections:
                if len(section.split()) < 300:
                    passages.append(section)
                else:
                    for para in section.split("\n"):
                        passages.append(para)
            # if num_words > 500:
            for psg in passages:
                if len(psg.split()) < 20:
                    continue
                yield psg,d["id"] 

            # if False:
            #     for i in range(math.ceil(num_words/500)):
            #         yield summary,text,d["id"]
            # else:
            #     yield summary,text,d["id"]

def convert_file_to_batch_files(filename):
    text_iterator = yield_text_from_wiki_attributes(filename)
    
    batch_files_basename = filename.split("/")[-1].replace(".gz","")
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
            filenames.append(s3_prefix + okey)
    return filenames

def process_files_parallel(file_list):
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    with mp.Pool(processes=args.num_processes) as pool:
        for filename in file_list:
            pool.apply_async(convert_file_to_batch_files, (filename,))

        pool.close()
        pool.join()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",type=int, default=1)
    parser.add_argument("--model",type=str,default="gpt-4o-mini")
    parser.add_argument("--input_dir",type=str,default=None)
    parser.add_argument("--outdir",type=str,default=None)

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    
    #example file_list
    # file_list = [
    #     "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0088.json.gz",
    #     "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0090.json.gz",
    #     "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0112.json.gz",
    #     "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0066.json.gz",
    #     "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0097.json.gz"
    # ]

    args = parse_args()

    file_list = list_s3_files(args.input_dir)
    # Path(args.outdir).mkdir(parents=True, exist_ok=True)
    # convert_file_to_batch_files(file_list[0])

    process_files_parallel(file_list)
