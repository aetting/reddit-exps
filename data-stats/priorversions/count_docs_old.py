import os
import smart_open


parentdir = "/home/ec2-user/proc_scripts/tokens-dd-seq/llama"

ct = 0
for filename in os.listdir(parentdir):
    if ".gz" not in filename: continue
    print(filename)
    with smart_open.open(os.path.join(parentdir,filename)) as f:
        for line in f:
            ct += 1
print(ct)

