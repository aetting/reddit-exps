import re
import os

parent = "/Users/allysone/Desktop/research/dolma/python/dolma/data/reddit_blocklists"

# for listname in ["sciencesubreddits","historysubreddits","politicssubreddits"]:

#     subslist = set()
#     print(listname)
#     with open(os.path.join(parent,f"{listname}.tsv")) as f:
#         for line in f:
#             if len(line.strip()) < 3:
#                 continue
#             subname = line.split()[0]
#             m = re.match("/*(r/)*(.+)",subname)
#             clean = m.groups()[1]
#             subslist.add(clean)
#             # print(clean)
#     with open(os.path.join(parent,f"{listname}.txt"),"w") as out:
#         for subname in subslist:
#             out.write(f"{subname}\n")

with open("/Users/allysone/Desktop/research/reddit/MMLU_topics_subreddits.txt") as f:
    subslist = set()
    for line in f:
        if "---" in line or len(line.strip()) < 3:
            continue
        m = re.match("/*(r/)*(.+)",line.strip())
        clean = m.groups()[1]
        subslist.add(clean)
    with open(os.path.join(parent,f"mmlu_topic_subreddits.txt"),"w") as out:
        for subname in subslist:
            out.write(f"{subname}\n")