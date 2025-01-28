from collections import defaultdict

with open("/Users/allysone/Desktop/research/reddit/mmlu_topic_analysis/topic_deltas.csv") as f:
    scoredict = defaultdict(dict)
    for line in f:
        topic,form,delta = line.strip().split(",")
        # if type(delta) not in (float,int):
        #     delta = -0.00
        scoredict[topic][form] = float(delta)
    print(scoredict)
    bad = []
    good = []
    for topic in scoredict:
        for form in ("rc","mc"):
            if form not in scoredict[topic]:
                scoredict[topic][form] = 0
        if max(scoredict[topic]["mc"],scoredict[topic]["rc"]) + min(scoredict[topic]["mc"],scoredict[topic]["rc"]) < 1:
        # if (scoredict[topic]["mc"] < 0.0 or scoredict[topic]["rc"] < 0.0):
            bad.append(f"{topic}: {scoredict[topic]['mc']} ; {scoredict[topic]['rc']}")
        else:
            good.append(f"{topic}: {scoredict[topic]['mc']} ; {scoredict[topic]['rc']}")

    print("BAD")
    for e in bad: print(e)

    print("\nGOOD")
    for e in good: print(e)
