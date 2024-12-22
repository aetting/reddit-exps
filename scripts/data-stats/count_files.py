import boto3    
import re

client = boto3.client('s3')
bucket = "ai2-llm"

def list_files():
    dirname = "dolma-orig-mix"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/source-added/attributes/dclmtag"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
    ct = 0
    comment_list = []
    sub_list = []
    for page in pages:
        for obj in page["Contents"]:
            if ".gz" not in obj["Key"]: continue
            okey = obj["Key"]
            ct += 1
            if "19307" in okey:
                comment_list.append(okey)
            elif "10060" in okey:
                sub_list.append(okey)
            else:
                print(f"ERROR: {okey}")
            # if ct > 50: break
    print(len(comment_list))
    print(len(sub_list))
    print(ct)
    return comment_list,sub_list


def check_consecutive(input_list):
    list_sort = sorted(input_list)
    prev = None
    print("%%%%\nNOW CHECKING\n%%%%")
    for i,e in enumerate(list_sort):
        m = re.match(".*raw-(.*)-of.*",e)
        num = int(m.groups()[0])
        if i > 0 and num != prev+1:
            print(f"ERROR {e}")
        prev = num

if __name__ == "__main__":
    comm,sub = list_files()
    check_consecutive(comm)
    check_consecutive(sub)

