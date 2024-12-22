import json
import smart_open
import gzip
from collections import defaultdict
import argparse
import boto3

import multiprocessing as mp

def assemble_convo_string(cid, thread, anonymous_author_lookup, nodes, level):
    if level == 50:
        return ''
    comment = thread[cid]
    convo_string = ''
    indent = ' ' * 4
    text = f"(SCORE: {comment['score']}) {comment['body']}"
    # author = anonymous_author_lookup[comment['author']]
    convo_string += f'{indent * level }#USER#: {text}\n\n'
    for child in sorted(nodes.get(cid, []), key=lambda x: thread[x]['score'], reverse=True):
        convo_string += assemble_convo_string(child, thread, anonymous_author_lookup, nodes, level + 1)
    return convo_string

def order_comments(thread, anonymous_author_lookup):
    nodes, roots = defaultdict(set), set()
    id_to_comment = {}
    for comment in thread:
        cid = comment["id"]
        id_to_comment[cid] = comment
        # if _should_skip(comment, 1):
        #     continue
        if comment['link_id'].split('_')[1] == comment['parent_id']:
            roots.add(cid)
        else:
            nodes[comment['parent_id']].add(cid)
    thread_string = ''
    for cid in sorted(roots, key=lambda x: id_to_comment[x]['score'], reverse=True):
        thread_string += assemble_convo_string(cid, id_to_comment, anonymous_author_lookup, nodes, 0)
    return thread_string

def check_deleted_comment(comment):
    if "[deleted]" in comment['body'] or "[removed]" in comment['body'] or "[UNICODE ENCODE ERROR]" in comment['body']:
        return True
    return False

def construct_metadata(post,select_comment_list):
    metadata = {
        "subreddit": post["subreddit"],
        "author": post["author"],
        "score": post["score"],
        "over_18": post["over_18"] if "over_18" in post else None,
        "stickied": post["stickied"] if "stickied" in post else None,
        "removed_by_category": post["removed_by_category"] if "removed_by_category" in post else None,
        "edited": post["edited"] if "edited" in post else None,
        "post_hint": post["post_hint"] if "post_hint" in post else None,
        "url": post["url"] if "url" in post else None,
        "permalink": post["permalink"] if "permalink" in post else None,
        "media": True if post["media"] else False,
        "num_comments": post["num_comments"],
        "num_selected_comments": len(select_comment_list),
        "comment_ids": [comment["id"] for comment in select_comment_list],
        "comment_scores": [comment["score"] for comment in select_comment_list],
        "comment_authors": [comment["author"] for comment in select_comment_list],
        "comment_edited": [comment["edited"] if "edited" in comment else None for comment in select_comment_list],
        "comment_stickied": [comment["stickied"] if "stickied" in comment else None for comment in select_comment_list]
    }
    return metadata

def write_dolma_format(lined,text,select_comment_list):
    metadata = construct_metadata(lined["post"],select_comment_list)
    dolma_object = {
        "text": text,
        "id": "_".join([lined["id"]] + [comm_id for comm_id in metadata["comment_ids"]]),
        "created": lined["created"],
        "added": lined["added"],
        "source": lined["source"],
        "metadata": metadata
    }

    return dolma_object

def keep_top_comment(comment_list):
    top_comment = None
    top_comment_score = float('-inf')
    for comment in comment_list:
        if comment['link_id'].split('_')[1] == comment['parent_id']:
            if comment["score"] is None:
                comment["score"] = 0
            curr_score = comment["score"]
            if curr_score > top_comment_score:
                if not check_deleted_comment(comment):
                    top_comment = comment
                    top_comment_score = curr_score
            elif curr_score == top_comment_score:
                if len(comment["body"]) > len(top_comment["body"]):
                    if not check_deleted_comment(comment):
                        top_comment = comment
                        top_comment_score = curr_score
    output = (top_comment["body"], [top_comment]) if top_comment else None
    return output

def qa_format(post,comment_list):
    output = keep_top_comment(comment_list)
    if not output:
        return [None]
    comment_text,select_comment_list = output
    text = f"{post['title']}\n\n"
    if post['body']:
        text += f"{post['body']}\n\n"
    text += f"{comment_text}"

    return [(text,select_comment_list)]

def keep_comments_above_k(comment_list, k):
    comments_to_keep = []
    for comment in comment_list:
        if comment['link_id'].split('_')[1] == comment['parent_id']:
            if comment["score"] is None:
                comment["score"] = 0
            curr_score = comment["score"]
            if curr_score > k:
                if not check_deleted_comment(comment):
                    comments_to_keep.append((comment["body"],[comment]))
    return comments_to_keep

def qa_format_all(post,comment_list):
    comments_to_keep = keep_comments_above_k(comment_list,0)
    for comment_text,select_comment_list in comments_to_keep:
        text = f"{post['title']}\n\n"
        if post['body']:
            text += f"{post['body']}\n\n"
        text += f"{comment_text}"

        yield (text,select_comment_list)


def convert_file(obj,write_dir,ordering_func):
    okey = obj["Key"]
    filename = okey.split("/")[-1]
    print(okey)
    with smart_open.open(f"s3://{bucket}/{okey}") as f, gzip.open(f"{write_dir}/{filename}","wt") as out:
        for line in f:
            lined = json.loads(line)
            if not (lined["post"] and lined["comments_list"]):
                continue
            for ordering_output in ordering_func(lined["post"],lined["comments_list"]):
                if not ordering_output:
                    continue
                text,select_comment_list = ordering_output
                dolma_object = write_dolma_format(lined,text,select_comment_list)
                out.write(json.dumps(dolma_object) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("num_processes",type=int)
    args = parser.parse_args()

    num_processes = args.num_processes
    client = boto3.client('s3')

    bucket = "ai2-llm"
    filedir = f"pretraining-data/sources/reddit/dolma_raw/merged_raw"
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=f"{filedir}/sharded_output")

    write_dir = f"/home/ec2-user/merged_qa"

    results = []
    with mp.Pool(processes=num_processes) as pool:
        for page in pages:
            for obj in page["Contents"]:
                result = pool.apply_async(convert_file, (obj,write_dir,qa_format))
                results.append(result)
        for result in results:
            result.get()

        pool.close()
        pool.join()
                