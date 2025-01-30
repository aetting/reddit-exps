import json
import smart_open
import argparse
import math

from pathlib import Path
import multiprocessing as mp

from transformers import GPT2Tokenizer

from format_rewriting_core import text_to_prompt, write_batch_files

#for converting to openai batch files, need to define an iterator that yields the raw text to be converted to prompts
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

def convert_file_to_batch_files(filename):
    text_iterator = yield_text_from_dolma_jsonl(filename)
    
    batch_files_basename = filename.split("/")[-1].replace(".json.gz","")
    tokenizer_for_length_estimates = GPT2Tokenizer.from_pretrained("gpt2")
    
    write_batch_files(text_iterator,batch_files_basename,args.model,args.outdir,tokenizer_for_length_estimates)

def process_files_parallel(file_list):
    with mp.Pool(processes=args.num_processes) as pool:
        for filename in file_list:
            pool.apply_async(convert_file_to_batch_files, (filename,))

        pool.close()
        pool.join()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_processes",type=int)
    parser.add_argument("--model",type=str,default="gpt-4o-mini")
    parser.add_argument("--outdir",type=str,default=None)

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    file_list = [
        "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0088.json.gz",
        "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0090.json.gz",
        "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0112.json.gz",
        "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0066.json.gz",
        "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0097.json.gz"
    ]

    args = parse_args()

    process_files_parallel(file_list)
