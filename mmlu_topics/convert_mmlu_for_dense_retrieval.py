import os
import csv
import re
import json
import argparse

letter_to_ind = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3
}

multi_answer = [
    'none of these', 
    'all of the above are true', 
    'a and b only', 
    'all of the options given are correct', 
    'both', 'a and c only', 
    'options a and b', 
    'a b and c', 
    '#name?', 
    'either', 
    '(a), (b), and (c) are part of the theory', 
    'b and c', 
    'any 2 of the above values', 
    'all of these options', 
    'a or b', 
    'all of the above are correct', 
    '(a) and (c)', 
    'both of the above', 
    'none of the above', 
    'none of the above are appropriate', 
    'neither of these', 
    'both b and c', 
    'a and d', 
    'a and c', 
    'all of the above answers are correct', 
    'all of the above', 
    'all of these', 
    '(b) (c) and (d)', 
    'both a and d are correct', 
    'all three structures', 
    'both of the interventions', 
    'neither a nor b', 
    'none of the above is a true statement', 
    'none of the above are true statements', 
    'both of these.', 
    'a and b', 
    'both of the options given are correct', 
    'both a and b', 
    'none is outside the family; all are electromagnetic waves', 
    '(a), (b), and (c)', 
    'both a and c', 
    'either of these', 
    'neither', 
    'both are the same', 
    'all of above', 
    'none of the above are false', 
    'either a or b', 
    'all of below', 
    'both (a) and (c)'
]

def concat_corr_only(csvreader,outdir,corename):
    with open(os.path.join(outdir,f"{corename}.jsonl"),"w") as out:
        for line in csvreader:
            q = line[0]
            a = line[-1]
            ops = line[1:-1]
            corr = ops[letter_to_ind[a]]
            if corr.strip().strip(".").lower() in multi_answer:
                ops.pop(letter_to_ind[a])
                outstr = f"{q} {'; '.join(ops)}"
            else:
                outstr = f"{q} {corr}\n"
            
            out.write(json.dumps({"text": outstr}) + "\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("question_dir",type=str)
    parser.add_argument("output_dir",type=str)
    args = parser.parse_args()

    question_dir = args.question_dir
    output_dir = args.output_dir

    os.makedirs(output_dir,exist_ok=True)

    for filename in os.listdir(question_dir):
        corename = filename.split(".")[0]
        with open(os.path.join(question_dir,filename), newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            concat_corr_only(csvreader,output_dir,corename)


