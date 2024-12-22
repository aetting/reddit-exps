dolma -c configs/dolma-threads-tok.yaml tokens \
	    --processes 192


aws s3 sync tokens-dd-seq/mmlu-dense-subs s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs/tokenized/

