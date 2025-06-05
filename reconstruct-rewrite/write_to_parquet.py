import pandas as pd
# import pyarrow as pa
# import pyarrow.parquet as pq

import fastparquet as fp

import json

# Create a sample DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'Salary': [50000, 60000, 70000]
})

def write_from_file(filename):

    with open(filename) as file:
        alldict = {}
        i = 0
        for line in file:
            i +=1
            if i > 10: break
            d = json.loads(line)
            alldict[i] = {"text":d["text"]}

    print(alldict)
    df = pd.DataFrame.from_dict(alldict,orient="index")

    # import pdb; pdb.set_trace()

    fp.write('/Users/allysone/Desktop/research/reddit/decoded_toks/parquet_test/test.parquet', df)


        # # Convert the DataFrame to an Arrow Table
        # table = pa.Table.from_pandas(df)

        # # Write the Arrow Table to a Parquet file
        # pq.write_table(table, 'sample.parquet')

if __name__ == "__main__":
    write_from_file("/Users/allysone/Desktop/research/reddit/decoded_toks/part-000-00000-decoded.jsonl")