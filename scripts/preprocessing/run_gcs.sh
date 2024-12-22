# python /Users/allysone/Desktop/research/dolma/sources/reddit/complete_threads_codelike_v4/build_combined_thread_data.py \
# --input_gcs_dir_comments /Users/allysone/Desktop/research/reddit/raw_sample/comments/reddit_raw_comments_split_RC_2005-12.aa.gz \
# --input_gcs_dir_submissions /Users/allysone/Desktop/research/reddit/raw_sample/submissions/reddit_raw_submissions_split_RS_2005-12.aa.gz \
# --output_dir /Users/allysone/Desktop/research/reddit/raw_sample/output

# python /Users/allysone/Desktop/research/dolma/sources/reddit/complete_threads_codelike_v4/build_combined_thread_data.py \
# --input_gcs_dir_comments gs://olmo-pretraining-data/reddit/raw/comments_test_small_multiple/*.gz \
# --input_gcs_dir_submissions gs://olmo-pretraining-data/reddit/raw/submissions_test_small_multiple/*.gz \
# --output_dir gs://olmo-pretraining-data/reddit/test_output \
# --runner DataflowRunner \
# --temp_location gs://olmo-pretraining-data/reddit/test_output/temp \
# --staging_location gs://olmo-pretraining-data/reddit/test_output/staging \
# --project ai2-olmo \
# --setup_file /Users/allysone/Desktop/research/dolma/sources/reddit/complete_threads_codelike_v4/setup.py

python /Users/allysone/Desktop/research/dolma/sources/reddit/complete_threads_codelike_v4/build_combined_thread_data.py \
--input_gcs_dir_comments gs://olmo-pretraining-data/reddit/raw/comments_split/*.gz \
--input_gcs_dir_submissions gs://olmo-pretraining-data/reddit/raw/submissions_split/*.gz \
--output_dir gs://olmo-pretraining-data/reddit/merged_raw \
--runner DataflowRunner \
--temp_location gs://olmo-pretraining-data/reddit/merged_raw/temp \
--staging_location gs://olmo-pretraining-data/reddit/merged_raw/staging \
--project ai2-olmo \
--setup_file /Users/allysone/Desktop/research/dolma/sources/reddit/complete_threads_codelike_v4/setup.py