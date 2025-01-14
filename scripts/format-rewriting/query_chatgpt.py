from openai import OpenAI
import os
from pydantic import BaseModel
import prompt_templates

from s3_functions import read_jsonl_from_s3

# Initialize your OpenAI API key
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)
# openai.organization = os.getenv("OPENAI_ORGANIZATION")

class MCQuestion(BaseModel):
    question: str
    options: list[str]
    answer: str

class Classification(BaseModel):
    answer: str

def get_responses(prompts, model="gpt-4o-mini", temperature=0.7, max_tokens=150):
    """
    Takes a list of prompts and submits them to the OpenAI API.
    Returns responses for each prompt.

    Args:
        prompts (list of str): A list of prompts to send to the API.
        model (str): OpenAI model to use (default is "gpt-4-turbo-mini").
        temperature (float): Sampling temperature for randomness.
        max_tokens (int): Maximum number of tokens to generate in each response.

    Returns:
        dict: A dictionary with prompts as keys and model responses as values.
    """
    responses = {}
    for prompt in prompts:
        try:
            # Call the OpenAI API
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": "You are a helpful assistant that outputs json."},
                          {"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            # Extract the response text
            # responses[prompt] = response['choices'][0]['message']['content'].strip()
            # responses[prompt] = response['choices'][0]['message']
            print(response.choices[0].message.content)
        except Exception as e:
            # Handle any errors
            responses[prompt] = f"Error: {str(e)}"
    return responses

def get_responses_structured(prompts, structure, model="gpt-4o-mini", temperature=0.7, max_tokens=150):
    """
    Takes a list of prompts and submits them to the OpenAI API.
    Returns responses for each prompt.

    Args:
        prompts (list of str): A list of prompts to send to the API.
        model (str): OpenAI model to use (default is "gpt-4-turbo-mini").
        temperature (float): Sampling temperature for randomness.
        max_tokens (int): Maximum number of tokens to generate in each response.

    Returns:
        dict: A dictionary with prompts as keys and model responses as values.
    """
    responses = {}
    for prompt in prompts:
        try:
            # Call the OpenAI API
            response = client.beta.chat.completions.parse(
                model=model,
                messages=[{"role": "system", "content": "You are a helpful assistant that outputs json."},
                          {"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=structure
            )
            # Extract the response text
            # responses[prompt] = response['choices'][0]['message']['content'].strip()
            responses[prompt] = response.choices[0].message.content
        except Exception as e:
            # Handle any errors
            responses[prompt] = f"Error: {str(e)}"
    return responses    


# Example usage
if __name__ == "__main__":
    prompts = []
    loc = "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/"
    file_keys = [
        os.path.join(loc,"merged_qa_prefilter_densesubs_highthresh-0000.json.gz")
        ] 

    template = prompt_templates.CHECK_ACADEMIC
    for i,line in enumerate(read_jsonl_from_s3(file_keys)):
        prompts.append(template.format(text=line["text"]))
        if i >= 30: break
    
    results = get_responses_structured(prompts,Classification)
    for prompt, response in results.items():
        print(f"Prompt: {prompt}\nResponse: {response}\n")



# get list of texts --> get file list (paginator or read from file list); extract json objs from each file and yield; extract text field
# create prompts from texts
# submit to ChatGPT

