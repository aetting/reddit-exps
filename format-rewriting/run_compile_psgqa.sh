python psgqa_output_to_dolma.py \
  --output_dir ~/psg_qa_fullout \
  --gen_input_dir s3://ai2-llm/pretraining-data/sources/wiki_psgqa_rewrites/raw_qa_generations_v1/ \
  --psg_input_dir s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/format_rewriting/wiki_psgqa_batches1/ \
  --num_processes 180
