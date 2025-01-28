import json
import os
import shutil

errors = []
with open("/home/ec2-user/batch_prompts_ht_mini/SENDSILVER_DATA") as f, open("/home/ec2-user/batchlog.txt","w") as out:
    d = json.load(f)
    # import pdb; pdb.set_trace()
    for e in d:
        if d[e]["state"] == "completed":
            out.write(str(d[e]) + "\n")
        else:
            errors.append(d[e])
    out.write("\n\nERRORS\n\n")
    for e in errors:
        out.write(str(e) + "\n")
        fname = e["filename"]
        shutil.copyfile(os.path.join("/home/ec2-user/batch_prompts_ht_mini/",fname),os.path.join("/home/ec2-user/batch_prompts_ht_mini_secondtry/",fname))

