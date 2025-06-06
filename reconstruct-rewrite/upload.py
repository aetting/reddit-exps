from huggingface_hub import HfApi
import os

api = HfApi(token=os.getenv("HF_TOKEN"))
api.upload_folder(
    folder_path="/home/ec2-user/reddit/decoded_toks/parquet_files",
    repo_id="aettinger/redditqa",
    repo_type="dataset",
)