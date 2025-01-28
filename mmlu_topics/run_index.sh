dolma-search index \
    -i indexed/merged_qa_all_prefiltered \
    -d "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_all_wsubreddit/merged_qa_all_prefilter/*.gz" \
    -n 4 \
    -N 12 \
    -b 1000 \
    -B 50000 \
    -f

# "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_subreddit_added/sharded_output-0000*.gz"
