import boto3    
import smart_open

client = boto3.client('s3')
bucket = "ai2-llm"

def list_files():
    dirname = "dolma-orig-mix"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/source-added/tokens-dd/{dirname}-toks"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
    ct = 0
    source_files_in_toks = []
    for page in pages:
        for obj in page["Contents"]:
            if ".gz" not in obj["Key"]: continue
            okey = obj["Key"]
            ct += 1
            if ct % 100 == 0: print(ct)
            with smart_open.open(f"s3://{bucket}/{okey}") as f:
                i = 0
                for line in f:
                    source = line.split(",")[3]
                    # print(source)
                    i += 1
                    if i == 1:
                        break
            source_files_in_toks.append(source)
            # if ct > 50: break
    print(len(source_files_in_toks))
    print(ct)

    filedir = f"pretraining-data/sources/reddit/dolma_raw/source-added/mixed-dd/{dirname}"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
    cts = 0
    source_files = []
    for page in pages:
        for obj in page["Contents"]:
            if ".gz" not in obj["Key"]: continue
            okey = obj["Key"]
            cts += 1
            source_files.append(okey)
    print(len(source_files))
    print(cts)

    sfit_sort = sorted(source_files_in_toks)
    with open("sfit.txt","w") as out:
        for e in sfit_sort:
            out.write(e + "\n")
    sf_sort = sorted(source_files)
    with open("sf.txt","w") as out:
        for e in sf_sort:
            out.write(e + "\n")

    # import pdb; pdb.set_trace()


def analyze_lists():
    sfit = []
    with open("sfit.txt") as f:
        for line in f:
            sfit.append(line.strip().replace("s3://ai2-llm/",""))
    sf = []
    with open("sf.txt") as f:
        for line in f:
            sf.append(line.strip())


    for i,e in enumerate(sfit):
        if e == sfit[i-1]:
            print(e)

if __name__ == "__main__":
    analyze_lists()

