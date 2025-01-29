import json
import smart_open

from pathlib import Path
import multiprocessing as mp

from transformers import GPT2Tokenizer

from format_rewriting_core import text_to_prompt, write_batch_files

#need to define an iterator function that yields the raw text to be converted to prompts
def yield_text_from_dolma_jsonl(filename):
    with smart_open.open(filename) as f:
        for line in f:
            d = json.loads(line.strip())
            if d["id"] in files_dict[source_doc]:
                text = d["text"]
                num_words = len(text.split())
                if num_words > 500:
                    for i in range(math.ceil(num_words/500)):
                        yield text,d["id"]
                else:
                    yield text,d["id"]


def convert_file_to_batch_files(filename):
    text_iterator = yield_text_from_dolma_jsonl(filename)
    
    batch_files_basename = filename.split("/")[-1].replace(".jsonl","")
    tokenizer_for_length_estimates = GPT2Tokenizer.from_pretrained("gpt2")
    
    write_batch_files(text_iterator,batch_files_basename,args.model,args.outdir,tokenizer_for_length_estimates)

def process_files_parallel(file_list):
    results = []
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    with mp.Pool(processes=args.num_processes) as pool:
        for filename in file_list:
            result = pool.apply_async(convert_file_to_batch_files, (file_list,))
            results.append(result)

        pool.close()
        pool.join()

if __name__ == "__main__":
    filelist = [
        "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0112.json.gz",
        "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/merged_qa_prefilter_densesubs_highthresh-0097.json.gz ",

    ]
    process_files_parallel(filelist)
