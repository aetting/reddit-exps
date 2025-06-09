from huggingface_hub import HfApi
import os

api = HfApi(token=os.getenv("HF_TOKEN"))
api.upload_folder(
    folder_path="/home/ec2-user/reddit/decoded_toks/upload_files-jsonl",
    repo_id="allenai/academic-qa-reddit",
    repo_type="dataset",
)