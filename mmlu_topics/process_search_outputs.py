import json
import os

import argparse

from pathlib import Path

from collections import Counter, defaultdict

def check_file_numbers(query_dir):
    for filename in os.listdir(query_dir):
        with(open(os.path.join(query_dir,filename))) as qf:
            qi = 0
            for line in qf:
                qi += 1
        with(open(os.path.join(search_outputs,f"{filename.split('.')[0]}.jsonl"))) as sf:
            si = 0
            for line in sf:
                si += 1
        print(f"{filename} -- {qi},{si}")
        if qi*10 != si:
            print("MISMATCH")
        print("%%%%")


def update_counts(this_sub,this_text,subdict,subcounts,overall_sub_counts,basename):
    subcounts[this_sub] += 1
    subdict[this_sub].append((this_sub,this_text))
    if this_sub not in overall_sub_counts:
        overall_sub_counts[this_sub] = {}
        overall_sub_counts[this_sub]["total_items"] = 0
        overall_sub_counts[this_sub]["all_cats"] = set()
    overall_sub_counts[this_sub]["total_items"] += 1
    overall_sub_counts[this_sub]["all_cats"].add(basename)

def extract_subreddit(retrieved_dict,subdict,subcounts,overall_sub_counts,basename,tot_per_cat,seen_text,dense=False,take_all=False):
    if dense:
        for retrieval in retrieved_dict["ctxs"]:
            tot_per_cat += 1
            this_sub = retrieval["subreddit"]
            this_text = retrieval["retrieval text"]
            if take_all:
                update_counts(this_sub,this_text,subdict,subcounts,overall_sub_counts,basename)
            else:
                if this_text not in seen_text:
                    seen_text.add(this_text)

                    update_counts(this_sub,this_text,subdict,subcounts,overall_sub_counts,basename)
    else:
        tot_per_cat += 1
        this_sub = retrieved_dict["document"]["subreddit"]
        this_text = retrieved_dict["document"]["text"]
        update_counts(this_sub,this_text,subdict,subcounts,overall_sub_counts,basename)

    return tot_per_cat

def get_top_subreddits(search_outputs,analysis_dir,dense=False,take_all=False):
    Path(analysis_dir).mkdir(parents=True, exist_ok=True)
    top_subs_by_cat = {}
    top_subs_overall = {}
    full_cat_summary = {}
    with open(os.path.join(analysis_dir,"top_subs_by_cat.txt"),"w") as top: 
        overall_sub_counts = {}
        for filename in os.listdir(search_outputs):
            tot_per_cat = 0
            basename = filename.split('.')[0]
            subdict = defaultdict(list)
            subcounts = Counter()
            full_cat_summary[basename] = {}
            seen_text = set()
            with open(os.path.join(search_outputs,filename)) as f:
                for line in f:
                    try:
                        retrieved_dict = json.loads(line)
                    except:
                        continue
                    tot_per_cat = extract_subreddit(retrieved_dict,subdict,subcounts,overall_sub_counts,basename,tot_per_cat,seen_text,dense=dense,take_all=take_all)
            subcounts_sorted = sorted(subcounts.items(),key = lambda x: x[1],reverse=True)
            full_cat_summary[basename]["subreddit_counts"] = subcounts
            full_cat_summary[basename]["total_items"] = tot_per_cat
            i = 0
            cat_ct = 0
            with open(os.path.join(analysis_dir,f"{basename}-subreddit_ranking.txt"),"w") as out:
                for sub,count in subcounts_sorted:
                    i += 1
                    out.write(f"{count}: {sub}\n")
                top.write(f"\n{filename} (total {tot_per_cat})\n")
                for sub,count in subcounts_sorted:
                    cat_ct += count
                    if count < 3:
                        top.write(f"Coverage: {cat_ct} ({cat_ct/tot_per_cat:2f})\n")
                        break
                    top.write(f"{count}: {sub}\n")
                    # if cat_ct/tot_per_cat > .8:
                    #     break
            with open(os.path.join(analysis_dir,f"{basename}-subreddit_contents.jsonl"),"w") as out:
                for sub,_ in subcounts_sorted:
                    for item in subdict[sub]:
                        out.write(json.dumps(item) + "\n")
    overall_sub_counts_sorted = sorted(overall_sub_counts.items(),key=lambda x:x[1]["total_items"],reverse=True)
    with open(os.path.join(analysis_dir,f"top_subs_overall.txt"),"w") as topfull:
        for sub,subctdict in overall_sub_counts_sorted:
            topfull.write(f"{sub}: {subctdict['total_items']}\n")
            topfull.write(f"{len(subctdict['all_cats'])} categories\n")
            topfull.write(f"{subctdict['all_cats']}\n\n")
    
    return overall_sub_counts_sorted,full_cat_summary

def select_subreddits(overall_sub_counts_sorted, full_cat_summary):
    # select top overall subs based on some threshold (overall_sub_counts_sorted)
    thresh = 40
    selected_subs = set()
    for sub,subctdict in overall_sub_counts_sorted:
        if subctdict['total_items'] >= thresh:
            selected_subs.add(sub)
    for sub in selected_subs: 
        print(sub)
    for cat in full_cat_summary:
        print(f"\n{cat}")
        cat_sub_counts = full_cat_summary[cat]["subreddit_counts"]
        cat_total_items = full_cat_summary[cat]["total_items"]
        cat_coverage = 0
        for sub in selected_subs:
            if sub in cat_sub_counts:
                cat_coverage += cat_sub_counts[sub]
                print(f"{sub}: {cat_sub_counts[sub]}")
        perc_coverage = cat_coverage/cat_total_items
        print(f"{cat}: coverage {cat_coverage}/{cat_total_items} ({perc_coverage:.2f})")
        
        # coverage_min = .75
        # if perc_coverage < coverage_min:
        subcounts_sorted = sorted(cat_sub_counts.items(),key = lambda x: x[1],reverse=True)
        for sub,count in subcounts_sorted:
            if sub not in selected_subs:
                if count >= 5:
                    selected_subs.add(sub)
                    cat_coverage += count
                    print(f"{sub}:{count}")
                # else:
                #     print(f"{sub}:{count}")
                perc_coverage = cat_coverage/cat_total_items
        print(f"{cat}: coverage {cat_coverage}/{cat_total_items} ({perc_coverage:.2f})")
    get_coverage_stats(full_cat_summary,selected_subs)
                    
def select_subreddits_simple(full_cat_summary,selected_subs_output):
    selected_subreddits = set()
    with open(selected_subs_output,"w") as out:
        out.write("ADDED SUBS BY CATEGORY\n\n")
        for cat in full_cat_summary:
            cat_sub_counts = full_cat_summary[cat]["subreddit_counts"]
            for sub in cat_sub_counts:
                if cat_sub_counts[sub] >= 5:
                    selected_subreddits.add(sub)
                    out.write(f"({cat}) {sub}: {cat_sub_counts[sub]}\n")
            out.write("\n")
        get_coverage_stats(full_cat_summary,selected_subreddits,out)
        out.write(f"\nFINAL SELECTED SUBREDDITS\n\nTOTAL: {len(selected_subreddits)}\n")
        for sub in selected_subreddits:
            out.write(sub + "\n")

def select_subreddits_highthresh(full_cat_summary,overall_sub_counts_sorted,selected_subs_output):
    selected_subreddits = set()
    with open(selected_subs_output,"w") as out:
        out.write("ADDED SUBS BY CATEGORY\n\n")
        for cat in full_cat_summary:
            cat_sub_counts = full_cat_summary[cat]["subreddit_counts"]
            for sub in cat_sub_counts:
                if cat_sub_counts[sub] >= 20:
                    selected_subreddits.add(sub)
                    out.write(f"({cat}) {sub}: {cat_sub_counts[sub]}\n")
            out.write("\n")
        for sub,statdict in overall_sub_counts_sorted:
            if sub not in selected_subreddits and statdict["total_items"] >= 100:
                selected_subreddits.add(sub)
                out.write(f"(overall) {sub}: {statdict['total_items']}\n")
        get_coverage_stats(full_cat_summary,selected_subreddits,out)
        out.write(f"\nFINAL SELECTED SUBREDDITS LIST\n\nTOTAL: {len(selected_subreddits)}\n")
        for sub in selected_subreddits:
            out.write(sub + "\n")

def get_coverage_stats(full_cat_summary,selected_subreddit,outfile):   
    outfile.write("\nNUMBER OF HITS PER SUB AND COVERAGE BY CATEGORY\n")
    for cat in full_cat_summary:
        outfile.write(f"\n{cat}\n")
        cat_coverage = 0
        cat_sub_counts = full_cat_summary[cat]["subreddit_counts"]
        cat_total_items = full_cat_summary[cat]["total_items"]
        for sub in selected_subreddit:
            if sub in cat_sub_counts:
                cat_coverage += cat_sub_counts[sub]
                outfile.write(f"{sub}: {cat_sub_counts[sub]}\n")
        perc_coverage = cat_coverage/cat_total_items
        outfile.write(f"{cat}: coverage {cat_coverage}/{cat_total_items} ({perc_coverage:.2f})\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("search_results_dir",type=str)
    parser.add_argument("analysis_output_dir",type=str)
    parser.add_argument("--subreddit_selection",type=str,default=None)
    parser.add_argument('--dense', action='store_true')
    parser.add_argument('--simple', action='store_true')
    parser.add_argument('--take_all', action='store_true')
    args = parser.parse_args()

    # query_dir = "/home/ec2-user/mmlu_topics/mmlu_queries/test_queries/mmlu_queries_corr"
    # check_file_numbers(query_dir)
 
    search_outputs = args.search_results_dir
    analysis_dir = args.analysis_output_dir
    overall_sub_counts_sorted, full_cat_summary = get_top_subreddits(search_outputs, analysis_dir, dense=args.dense, take_all=args.take_all)
    
    # select_subreddits(overall_sub_counts_sorted, full_cat_summary)
    if args.subreddit_selection:
        if args.simple:
            select_subreddits_simple(full_cat_summary,args.subreddit_selection)
        else:
            select_subreddits_highthresh(full_cat_summary,overall_sub_counts_sorted,args.subreddit_selection)


