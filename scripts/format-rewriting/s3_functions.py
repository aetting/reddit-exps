import boto3
import json
import smart_open
import re
from collections import defaultdict


def return_json_objs_from_s3_files(filename_list):
    for filenane in filename_list:
        with smart_open.open(filename) as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    yield json.loads(line)


def extract_from_csv(csvfile):
    json_dict = {}
    files_dict = defaultdict(list)
    with smart_open.open(csvfile) as f:
        for line in f:
            start, stop, idx, docname, lineid = line.strip().split(",")
            files_dict[docname].append(idx)
    for source_doc in files_dict:
        print(source_doc)
        print(files_dict[source_doc])
        with smart_open.open(source_doc) as f:
            for line in f:
                d = json.loads(line.strip())
                json_dict[d["id"]] = d["text"]
        print(jsonlist)
        break



        

def get_doc_list_from_tokenized(config,strmatch,limit=-1):
    doclist = []
    pattern = r".*(s3://.*" + re.escape(strmatch) + r".*)\.npy"
    with open(config) as f:
        for line in f:
            m = re.match(pattern,line)
            if m:
                csvfile = m.groups()[0] + ".csv.gz"
                extract_from_csv(csvfile)


def read_jsonl_from_s3(file_keys):
    """
    Reads JSONL files from S3 and returns each line as a Python dictionary.

    :param bucket_name: Name of the S3 bucket.
    :param file_keys: List of S3 keys (filenames) to process.
    :return: Generator yielding each line as a dictionary.
    """
    # s3 = boto3.client('s3')
    
    for file_key in file_keys:
        print(f"Processing file: {file_key}")
        # response = s3.get_object(Bucket=bucket_name, Key=file_key)
        # content = response['Body'].read().decode('utf-8')
        with smart_open.open(file_key) as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    yield json.loads(line)

if __name__ == "__main__":
    config = "/Users/allysone/Desktop/research/OLMo/configs/reddit_microannealing/peteish7-weka-microanneal-from928646_reddit-merged_qa_prefilter_densesubs_highthresh.yaml"
    strmatch = "merged_qa_prefilter/merged_qa_prefilter_densesubs"
    get_doc_list_from_tokenized(config,strmatch)
