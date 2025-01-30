from openai import OpenAI
client = OpenAI()


def upload_batch_file(filepath):
    batch_input_file = client.files.create(
                file=open(filepath, "rb"),
                    purpose="batch"
                    )

    print(batch_input_file)
    return(batch_input_file)

def create_batch(batch_input_file):
    # batch_input_file_id = batch_input_file.id
    m = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "write mcqs"
        }
    )
    print(m)
    return(m)

def check_status(batch_id):
    batch = client.batches.retrieve(batch_id)
    print(batch)

def retrieve_results(output_file_id):
    with open("/home/ec2-user/test_batch_output.jsonl","w") as out:
        file_response = client.files.content(output_file_id)
        out.write(file_response.text)   

if __name__ == "__main__":
    filepath = "/home/ec2-user/TEST_BATCH_FILE.jsonl"
    # batch_input_file = upload_batch_file(filepath)

    # FileObject(id='file-N1t2sjUJCWPay9yD5xhi3G', bytes=554893, created_at=1737157822, filename='TEST_BATCH_FILE.jsonl', object='file', purpose='batch', status='processed', status_details=None)
    input_file_id = "file-N1t2sjUJCWPay9yD5xhi3G"
    input_file_id = batch_input_file.id
    # batch_object = create_batch(input_file_id)

    # Batch(id='batch_678aedd64c208190bb5ad3d0e9457ce3', completion_window='24h', created_at=1737158102, endpoint='/v1/chat/completions', input_file_id='file-N1t2sjUJCWPay9yD5xhi3G', object='batch', status='validating', cancelled_at=None, cancelling_at=None, completed_at=None, error_file_id=None, errors=None, expired_at=None, expires_at=1737244502, failed_at=None, finalizing_at=None, in_progress_at=None, metadata={'description': 'write mcqs'}, output_file_id=None, request_counts=BatchRequestCounts(completed=0, failed=0, total=0))
    batch_id = "batch_678aedd64c208190bb5ad3d0e9457ce3"
    batch_id = batch_object.id
    # check_status(batch_id)

    output_file_id = "file-7AqnKGgpE2Ma9a5e8KPoeK"
    retrieve_results(output_file_id)
