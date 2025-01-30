python get_prompts_from_microanneal.py \
    --num_processes 5 \
    --config microanneal_configs/peteish7-weka-microanneal-from928646_reddit-merged_qa_prefilter_densesubs_highthresh.yaml \
    --tokfilepattern merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh \
    --outdir /home/ec2-user/prompt_script_test_2 \
    --model gpt-4o-mini
    # --needs_doc_insertion
