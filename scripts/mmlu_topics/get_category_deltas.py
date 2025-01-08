import json
import boto3
import smart_open
import os
import re

import numpy as np
# import process_search_outputs

baseline_results="s3://ai2-llm/evaluation/anneal-peteish-7b/OLMo-medium_peteish7_step928646-hf/"
anneal_results="s3://ai2-llm/evaluation/olmo-reddit/OLMo-medium_peteish7-microanneals_peteish7-weka-microanneal-from928646_reddit-merged_qa_prefilter_densesubs_step4802-hf/"
manual_anneal_results="s3://ai2-llm/evaluation/microanneal-peteish-7b/OLMo-medium_peteish7-microanneals_peteish7-weka-microanneal-from928646_reddit-v1_step740-hf/"

def get_scores(s3_dir):
    client = boto3.client('s3')
    bucket = "ai2-llm"
    paginator = client.get_paginator('list_objects_v2')
    filedir = s3_dir.split(f"{bucket}/")[1]
    pages = paginator.paginate(Bucket=bucket, Prefix=filedir)
    # import pdb; pdb.set_trace()

    all_scores = {}
    for page in pages:
        for obj in page["Contents"]:
            okey = obj["Key"]
            eval_folder = obj["Key"].split("/")[-2]
            obj_name = obj["Key"].split("/")[-1]
            if "mmlu" not in eval_folder:
                continue
            if obj_name != "metrics.json":
                continue
            with smart_open.open(f"s3://{bucket}/{okey}") as metricsfile:
                metrics = json.load(metricsfile)
                for topic_score in metrics["all_primary_scores"]:
                    topic,score = topic_score.split("::olmes: ")
                    if "mmlu_" not in topic:
                        continue
                    all_scores[topic] = float(score)
    return all_scores

def compare_scores(newdir,baselinedir):
    newdir_scores = get_scores(newdir)
    baselinedir_scores = get_scores(baselinedir)
    all_comparisons = {}
    for k in baselinedir_scores:
        if ":mc" not in k:
            continue
        newscore = newdir_scores[k]
        basescore = baselinedir_scores[k]
        delta = newscore - basescore
        topic_name = k.replace(":mc","")
        topic_name = topic_name.replace("mmlu_","")
        all_comparisons[topic_name] = (delta,newscore,basescore)
    comp_sorted = sorted(all_comparisons.items(), key = lambda x: x[1][0], reverse=True)
    return comp_sorted


def get_subreddit_stats():
    analysis_dir = "/home/ec2-user/mmlu_topics/subreddit_analysis/test_queries/mmlu_queries_corr/dense_merged_qa"
    with open(f"{analysis_dir}/top_subs_by_cat.txt") as f:
        topic = None
        coverages = {}
        sub_nums = {}
        for line in f:
            if len(line.strip()) == 0: continue
            if "retrieved_results.jsonl" in line:
                topic = line.split("_test_retrieved")[0]
                num_subs = 0
                line.strip()
            elif "Coverage:" in line:
                coverages[topic] = line.strip()
                sub_nums[topic] = num_subs
            else:
                num_subs += 1
    return coverages,sub_nums

def get_retrieval_scores():
    search_outputs = "/home/ec2-user/mmlu_topics/search_outputs_dense/merged_qa_prefilter_mmlu_retrieved"
    all_scores = {}
    mean_scores = {}
    for filename in os.listdir(search_outputs):
        basename = filename.split("_test_retrieved")[0]
        all_scores[basename] = {}
        with open(os.path.join(search_outputs,filename)) as f:
            for line in f:
                d = json.loads(line)
                for retrieval in d["ctxs"]:
                    sub = retrieval["subreddit"]
                    if sub not in all_scores[basename]:
                        all_scores[basename][sub] = []
                    all_scores[basename][sub].append(float(retrieval["retrieval score"]))
        mean_scores[basename] = []
        for sub in all_scores[basename]:
            total_retrieved = len(all_scores[basename][sub])
            mean_score = np.mean(all_scores[basename][sub])
            mean_scores[basename].append((sub,mean_score,total_retrieved))
        mean_scores[basename] = sorted(mean_scores[basename],key = lambda x: x[2],reverse=True)

    return mean_scores

def get_subreddit_counts():
    subcounts = "/home/ec2-user/reddit-exps/scripts/data-stats/output_count_files/output_count_files/subreddit_counts/densesubs_subredditcount.txt"
    subcountdict = {}
    with open(subcounts) as f:
        for line in f:
            m = re.match("(.*)\: d = ([0-9]+)",line)
            if not m:
                continue
            sub,count = m.groups()
            subcountdict[sub] = int(count)
    return subcountdict

comparison_sorted = compare_scores(anneal_results,baseline_results)
coverages, num_subs = get_subreddit_stats()
retrieval_mean_scores = get_retrieval_scores()
subcountdict = get_subreddit_counts()
# import pdb; pdb.set_trace()

for topic,scores in comparison_sorted:
    print(f"{topic}: {scores} -- {coverages[topic]}; maxsub: {retrieval_mean_scores[topic][0][2]} ; #subs {num_subs[topic]}")
    # print(retrieval_mean_scores[topic][:10])
    subratios = []
    subratio_vals = []
    for x in retrieval_mean_scores[topic][:10]:
        sub = x[0]
        catcount = x[2]
        if catcount < 5:
            continue
        subtotal = subcountdict.get(x[0],None)
        ratio = x[2] / subtotal if subtotal else None
        subratios.append(f"{sub}: {ratio} ({catcount} / {subtotal})")
        subratio_vals.append(ratio)
    print(f"max ratio: {max(subratio_vals)} ; min ratio: {min(subratio_vals)}")
    print(subratios)
    print()



