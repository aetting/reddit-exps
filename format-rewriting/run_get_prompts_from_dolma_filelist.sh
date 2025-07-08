python get_prompts_from_dolma_filelist.py \
    --num_processes 5 \
    --input_dir s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_lowthresh/documents/ \
    --outdir /home/ec2-user/prompt_script_test \
    --model gpt-4o-mini
