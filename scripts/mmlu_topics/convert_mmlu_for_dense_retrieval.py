import os
import csv
import re
import json

question_dir = "/net/nfs.cirrascale/allennlp/allysone/reddit/mmlu/mmlu_data/test"
# with open('eggs.csv', newline='') as csvfile:
#     spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')

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
# l = [
#     "All of these",
#     "None of these",
#     "Both",
#     "Neither",
#     "Either"
#     "Both of these."
#     "Neither of these",
#     "Either of these",
#     "Both are the same",
#     Both b and c
#     ALL of the above
#     "All of the above"
#     All of the above are true.
#     All of these options.
#     "None of the above"
#     Both of the above.
#     Both b and c
#     both A and B
#     Both A and C
#     Both A and B
#     all of below.
#     all of above.
#     A and D
#     A and B only
#     A and C only
#     A B and C
#     A and B
#     (A), (B), and (C)
#     (A), (B), and (C) are part of the theory
#     "#NAME?"
#     (A) and (C)
#     (B) (C) and (D).
#     both A and D are correct.
#     both (A) and (C)
#     A and C
#     b and c
#     Any 2 of the above values
#     Options A and B
#     a or b
#     all three structures.
#     either A or B
#     both B and C
#     All of the above answers are correct.
#     None of the above are appropriate.
#     None of the above are true statements.
#     None of the above are false.
#     None of the above is a true statement.
#     Both of the options given are correct.
#     All of the options given are correct
#     Both a and c
#     Both of the interventions
#     All of the above are correct.
#     neither a nor b
#     None is outside the family; all are electromagnetic waves
# ]


def concat_corr_only(csvreader):
    outdir = "/net/nfs.cirrascale/allennlp/allysone/reddit/mmlu/mmlu_queries/test_queries/mmlu_queries_corr"
    with open(os.path.join(outdir,f"{corename}.jsonl"),"w") as out:
        i = 0
        for line in csvreader:
            # if i >= 20:
            #     break
            # i += 1
            q = line[0]
            a = line[-1]
            ops = line[1:-1]
            corr = ops[letter_to_ind[a]]
            if corr.strip().strip(".").lower() in multi_answer:
                ops.pop(letter_to_ind[a])
                outstr = f"{q} {'; '.join(ops)}"
            else:
                outstr = f"{q} {corr}\n"
            
            # nonasciis = []
            # for c in outstr:
            #     if not c.isascii():
            #         nonasciis.append(c)
    
            # for to_remove in nonasciis:
            #     outstr = outstr.replace(to_remove,"")
            # for to_remove in [":","[","]","(",")","^","{","}",'"']:
            #     outstr = outstr.replace(to_remove,"")
            # for to_remove in ["+","-",">","<","\n"]:
            #     outstr = outstr.replace(to_remove," ")
            # for to_remove in ["AND","OR","IN"]:
            #     outstr = outstr.replace(to_remove,to_remove.lower())
            # if outstr.startswith("'"):
            #     outstr = outstr[1:]
            # out.write(' '.join(outstr.split()) + "\n")
            out.write(json.dumps({"text": outstr}) + "\n")

# def keep_all_options(csvreader):
#     outdir = "/home/ec2-user/mmlu_topics/mmlu_queries/test_queries/mmlu_queries_all"
#     with open(os.path.join(outdir,f"{corename}.txt"),"w") as out:
#         for line in csvreader:
#             for outstr in line[:-1]:
#                 for to_remove in [":","[","]","(",")","^","{","}",'"']:
#                     outstr = outstr.replace(to_remove,"")
#                 for to_remove in ["+","-",">","<"]:
#                     outstr = outstr.replace(to_remove," ")
#                 out.write(outstr + "\n")

# def q_vs_ops(csvreader):
#     outdir = "/home/ec2-user/mmlu_topics/mmlu_queries/test_queries/mmlu_queries_qvo"
#     with open(os.path.join(outdir,f"{corename}.txt"),"w") as out:
#         for line in csvreader:
#             strings_to_output = []
#             q = line[0]
#             ops = line[1:-1]
#             strings_to_output.append(q)
#             if min(len(op.split()) for op in ops) < 5:
#                 strings_to_output.append(' '.join(ops))
#             else:
#                 for op in ops:
#                     strings_to_output.append(op)
#                 #put them into the list separately. then iterate over the list and remove bad chars
#             for outstr in strings_to_output:
#                 if "abstract" in corename:
#                     print(outstr)
#                 for to_remove in [":","[","]","(",")","^","{","}",'"']:
#                     outstr = outstr.replace(to_remove,"")
#                 for to_remove in ["+","-",">","<"]:
#                     outstr = outstr.replace(to_remove," ")
#                 out.write(outstr + "\n")

# def q_vs_ops(csvreader):
#     outdir = "/home/ec2-user/mmlu_topics/mmlu_queries/test_queries/mmlu_queries_qvo"
#     with open(os.path.join(outdir,f"{corename}.txt"),"w") as out:
#         for line in csvreader:
#             strings_to_output = []
#             q = line[0]
#             ops = line[1:-1]
#             strings_to_output.append(q)
#             if min(len(op.split()) for op in ops) < 5:
#                 strings_to_output.append(' '.join(ops))
#             else:
#                 for op in ops:
#                     strings_to_output.append(op)
#                 #put them into the list separately. then iterate over the list and remove bad chars
#             for outstr in strings_to_output:
#                 if "abstract" in corename:
#                     print(outstr)
#                 for to_remove in [":","[","]","(",")","^","{","}",'"']:
#                     outstr = outstr.replace(to_remove,"")
#                 for to_remove in ["+","-",">","<"]:
#                     outstr = outstr.replace(to_remove," ")
#                 out.write(outstr + "\n")

for filename in os.listdir(question_dir):
    print("\n" + filename + "\n")
    corename = filename.split(".")[0]
    print(corename)
    with open(os.path.join(question_dir,filename), newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        concat_corr_only(csvreader)
        # keep_all_options(csvreader)
        # q_vs_ops(csvreader)


