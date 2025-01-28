import re
import boto3

client = boto3.client('s3')

bucket = "ai2-llm"
def check_objects(subdir):
    # filedir = f"pretraining-data/sources/reddit/dolma_raw/source-added/attributes/taggersec2/{subdir}"
    filedir = "pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa/documents"
    paginator = client.get_paginator('list_objects_v2')
    # pages = paginator.paginate(Bucket=bucket, Prefix=f"{filedir}/raw")
    pages = paginator.paginate(Bucket=bucket, Prefix=filedir)

    normal = []
    other = []
    tot = 0
    for page in pages:
        for obj in page["Contents"]:
            okey = obj["Key"]
            filename = okey.split("/")[-1]
            tot += 1
            m = re.match("sharded_.*",filename)
            if m: 
                normal.append(filename)
            else:
                print(okey)
                other.append(filename)
        normsort = sorted(normal)
    import pdb; pdb.set_trace()
    for i in range(1,len(normsort)):
        c = normsort[i]
        prev = normsort[i-1]
        if int(re.match("sharded_output-(.*)-of-.*",c).groups()[0]) != int(re.match("sharded_output-(.*)-of-.*",prev).groups()[0]) + 1:
            print(c)
        # import pdb; pdb.set_trace()
    print(f"TOTAL: {tot}")

# for s in ["comments","submissions"]:
#     print(f"%%%%%%%%%\n{s}\n%%%%%%%%%")
#     check_objects(s)

check_objects(1)
