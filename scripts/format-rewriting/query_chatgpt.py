from openai import OpenAI
import os
from pydantic import BaseModel
import prompt_templates
import json

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

class QuestionList(BaseModel):
    academic_relevance: bool
    questions: list[MCQuestion]

class TrueFalse(BaseModel):
    true: list[str]
    false: list[str]
    academic_relevance: bool

def get_responses(prompts, model="gpt-4o-mini", temperature=0.7, max_tokens=500):
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

def get_responses_structured(prompts, structure, model="gpt-4o-mini", temperature=0.7, max_tokens=800):
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
    # prompts = []
    # loc = "s3://ai2-llm/pretraining-data/sources/reddit/dolma_raw/merged_versions/merged_qa_wsubreddit/merged_qa_prefilter/merged_qa_prefilter_densesubs_highthresh/documents/"
    # file_keys = [
    #     os.path.join(loc,"merged_qa_prefilter_densesubs_highthresh-0000.json.gz")
    #     ] 
    
    # for i,line in enumerate(read_jsonl_from_s3(file_keys)):
    #     prompts.append(template.format(text=line["text"]))
    #     if i >= 30: break
    
    
    prompts = [
        "If you could only eat cuisine from 2 countries, which ones would you choose?\n\nItalian and Indian.",
        """ELI5: How does the socialism in Venezuela differ from Democratic Socialism?

First of you have to remember that socialism, democratic socialism, social democracies, etc. describe ideologies and streams of thoughts about what constitutes good policies and governments. They are not however manuals that you have to follow 100%.

Just like two countries with market economies are not the same, so do socialist countries.

With that said, Venezuela is not a democracy, even though they might like to say that, it's pretty clear that they are pretty close to a dictatorship.

Democratic socialism or social democracies are normal democracies, they do not have a drastically different from of government (e.g. Germany, Sweden, France, etc. are social democracies).

However they have a specific view on the role of government in the economy and how to improve the lives of all citizens.

In contrast to capitalism both Socialism and DemSoc believe in stronger regulation and taxes, in welfare programs and in strengthening workers opposed to owners.

A big difference between the two philosophies is that Socialism believes in a planned economy, where the government prescribes prices, production capacities, etc. basically tightly controlling the whole market place.

DemSocs "merely" believe that a free market needs to be regulated in a way that everybody profits. This means more things like minimum wages, welfare programs, etc. but no direct interference in how companies do their business."""
    ]

    template = prompt_templates.STATEMENT_TRUTH
    prompts = [template.format(text=p,num="two") for p in prompts]
    
    results = get_responses_structured(prompts,TrueFalse)
    for prompt, response in results.items():
        # print(f"Prompt: {prompt}")
        d = json.loads(response)
        # for q in d["questions"]:
        #     print(f"Question: {q}\n")
        print(d)
        print("\n~~~~~~\n")



# get list of texts --> get file list (paginator or read from file list); extract json objs from each file and yield; extract text field
# create prompts from texts
# submit to ChatGPT

