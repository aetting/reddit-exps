import re

with open("output-dolma-afterfix2.log") as f:
    comments = []
    submissions = []
    other = []
    for line in f:
        m = re.match(".*Downloading s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/documents/(.*) to af2mixtmpd.*",line)
        if m: 
            filename = m.groups()[0]
            if re.match(".*comments/raw-",filename):
                clean_string = filename.replace("comments/raw-","")
                comments.append(clean_string)
            elif re.match(".*submissions/raw-",filename):
                clean_string = filename.replace("submissions/raw-","")
                submissions.append(clean_string)
            else:
                other.append(filename)
    commentsort = sorted(comments)
    subsort = sorted(submissions)
    for i in range(1,len(commentsort)):
        c = commentsort[i]
        prev = commentsort[i-1]
        if int(c.replace("-of-19307.jsonl.gz","")) != int(prev.replace("-of-19307.jsonl.gz","")) + 1:
            print(c)
    for i in range(1,len(subsort)):
        c = subsort[i]
        prev = subsort[i-1]
        if int(c.replace("-of-10060.jsonl.gz","")) != int(prev.replace("-of-10060.jsonl.gz","")) + 1:
            print(c)
    import pdb; pdb.set_trace()
