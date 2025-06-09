import pandas as pd
# import pyarrow as pa
# import pyarrow.parquet as pq

import fastparquet as fp

import json
import os
import multiprocessing as mp

import gzip

# Create a sample DataFrame
# df = pd.DataFrame({
#     'Name': ['Alice', 'Bob', 'Charlie'],
#     'Age': [25, 30, 35],
#     'Salary': [50000, 60000, 70000]
# })

def write_from_file(fileset,naming_ind,indir,outdir):
    alldict = {"id":[],"text":[],"source":[]}
    with gzip.open(f"{outdir}-jsonl/reddit-rewrites-{naming_ind:04.0f}.jsonl.gz","wt") as jsonout:
        for filename in fileset:
            i = 0
            with open(os.path.join(indir,filename)) as file:
                for line in file:
                    i +=1
                    # if i > 10: break
                    d = json.loads(line)
                    # alldict["id"].append(d["id"])
                    # alldict["text"].append(d["text"])
                    # alldict["source"].append(filename)
                    jsonout.write(json.dumps({"id": d["id"],"text":d["text"]}) + "\n")

    # print(alldict)
    # df = pd.DataFrame.from_dict(alldict)
    # df.to_parquet(f"{outdir}-parquet/reddit-rewrites-{naming_ind}.parquet",index=False)

    # import pdb; pdb.set_trace()

    # fp.write(f"{outdir}/reddit-rewrites-{naming_ind}.parquet", df)


        # # Convert the DataFrame to an Arrow Table
        # table = pa.Table.from_pandas(df)

        # # Write the Arrow Table to a Parquet file
        # pq.write_table(table, 'sample.parquet')

if __name__ == "__main__":
    decoded_dir = "/home/ec2-user/reddit/decoded_toks"
    outdir = "/home/ec2-user/reddit/decoded_toks/upload_files"

    os.makedirs(outdir,exist_ok=True)
    os.makedirs(outdir+"-jsonl",exist_ok=True)


    all_files = [f for f in os.listdir(decoded_dir) if f.endswith("decoded.jsonl")]
    all_files = sorted(all_files)
    n = 4
    naming_ind = 0
    # for i in range(0,len(all_files),n):
    #     # if i > 5: break
    #     fileset = all_files[i:i+n]
    #     print(fileset)
    #     # print(os.path.join(decoded_dir,filename))
    #     write_from_file(fileset,naming_ind,decoded_dir,outdir)
    #     naming_ind += 1
    results = []
    with mp.Pool(processes=42) as pool:
        for i in range(0,len(all_files),n):
            fileset = all_files[i:i+n]
            print(fileset)
            # print(os.path.join(decoded_dir,filename))
            # write_from_file(fileset,naming_ind,decoded_dir,outdir)
            result = pool.apply_async(write_from_file, (fileset,naming_ind,decoded_dir,outdir))
            results.append(result)
            naming_ind += 1
        # docsum = 0
        # toksum = 0
        # with open(f"{subdir}_tokenized_doccount.txt","w") as out:
        # s = set()
        # for result in results:
        #     docslist = result.get()
        #     s = s.union(docslist)
        #         out.write(f"d = {docs}  ; t = {toks}\n")
        #     out.write(f"\n\n%%%%%%%%%%%%%\ndocs: {docsum}\n----\ntoks: {toksum}\n%%%%%%%%%%%%%")

        # print(s)
        # print(len(s))
        pool.close()
        pool.join()
