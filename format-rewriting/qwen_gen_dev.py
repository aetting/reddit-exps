from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import random
import json
import argparse

from psg_qa_prompt_templates import *

def generate_text_with_qwen(prompt, max_length=512, temperature=0.7, do_sample=True):
    """
    Generate text using Qwen 32B Instruct model
    
    Args:
        prompt (str): Input text prompt
        max_length (int): Maximum length of generated text
        temperature (float): Sampling temperature (higher = more creative)
        do_sample (bool): Whether to use sampling or greedy decoding
    
    Returns:
        str: Generated text
    """
    
    # Prepare the prompt in chat format
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    
    # Apply chat template
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # Tokenize input
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    # Generate text
    print("Generating text...")
    with torch.no_grad():
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=max_length,
            temperature=temperature,
            do_sample=do_sample,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode generated text
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

def load_model_tokenizer(model_name):
    # Load model and tokenizer
    
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,  # Use half precision to save memory
        device_map="auto",          # Automatically distribute across available GPUs
        trust_remote_code=True
    )

    return model,tokenizer

def parse_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument("--num_processes",type=int, default=1)
    # parser.add_argument("--model",type=str,default="gpt-4o-mini")
    parser.add_argument("--input_file",type=str,default=None)
    # parser.add_argument("--outdir",type=str,default=None)

    args = parser.parse_args()

    return args


# Example usage
if __name__ == "__main__":

    model_name = "Qwen/Qwen3-32B"
    model,tokenizer = load_model_tokenizer(model_name)


    psgs=["""The Daily News Building (also the News Building) is a skyscraper at 220 East 42nd Street in the East Midtown neighborhood of Manhattan, New York City, United States. The original tower, designed by Raymond Hood and John Mead Howells in the Art Deco style and completed in 1930, was one of several major developments constructed on 42nd Street around that time. A similarly-styled expansion, designed by Harrison & Abramovitz, was completed in 1960. When it originally opened, the building received mixed reviews and was described as having a utilitarian design. The Daily News Building is a National Historic Landmark, and its exterior and lobby are New York City designated landmarks.

The edifice occupies a rectangular site adjoined by 41st Street to the south, Second Avenue to the east, and 42nd Street to the north. It consists of a 36-story tower rising 476 feet (145 m), along with a 14-story printing plant on 41st Street and an 18-story annex on 42nd Street. There is a large carved-granite entrance at 42nd Street, leading to a rotunda lobby with a rotating painted globe. The facade is divided vertically into bays of windows separated by white-brick sections of wall, with brick spandrel panels between windows on different stories. The massing, or general shape, includes several setbacks on higher floors.""",
"""The Immaculate Reception is one of the most famous plays in the history of American football. It was a touchdown which occurred in the AFC divisional playoff game of the National Football League (NFL), between the Pittsburgh Steelers and the Oakland Raiders at Three Rivers Stadium in Pittsburgh, Pennsylvania, on December 23, 1972.

With his team trailing 7-6, on fourth down with 22 seconds left in the game, Steelers quarterback Terry Bradshaw threw a pass targeting Steelers running back John Fuqua. The ball bounced off the helmet of Raiders safety Jack Tatum. Steelers fullback Franco Harris caught it just before it hit the ground and ran for a game-winning touchdown. The play has been a source of some controversy and speculation ever since, with some contending that the ball touched only Fuqua (and did not in any way touch Tatum) or that it hit the ground before Harris caught it, either of which would have resulted in an incomplete pass by the rules of the time. Kevin Cook's The Last Headbangers cites the play as the beginning of a bitter rivalry between the Steelers and the Raiders that fueled a historically brutal Raiders team during the NFL's most controversially physical era""",
"""The Soviets hoped to foster pro-Soviet forces in East Asia to fight against anti-communist countries, particularly Japan. They attempted to contact the warlord Wu Peifu but failed.[21][22] The Soviets then contacted the Kuomintang (KMT), which was leading the Guangzhou government parallel to the Beiyang government. On 6 October 1923, the Comintern sent Mikhail Borodin to Guangzhou, and the Soviets established friendly relations with the KMT. The Central Committee of the CCP,[23] Soviet leader Joseph Stalin,[24] and the Comintern[25] all hoped that the CCP would eventually control the KMT and called their opponents "rightists".[26][note 3] KMT leader Sun Yat-sen eased the conflict between the communists and their opponents. CCP membership grew tremendously after the 4th congress in 1925, from 900 to 2,428.[28] The CCP still treats Sun Yat-sen as one of the founders of their movement and claim descent from him[29] as he is viewed as a proto-communist[30] and the economic element of Sun's ideology was socialism.[31] Sun stated, "Our Principle of Livelihood is a form of communism".[32]

The communists dominated the left wing of the KMT and struggled for power with the party's right-wing factions.[26] When Sun Yat-sen died in March 1925, he was succeeded by a rightist, Chiang Kai-shek, who initiated moves to marginalize the position of the communists.[26] Chiang, Sun's former assistant, was not actively anti-communist at that time,[33] even though he hated the theory of class struggle and the CCP's seizure of power.[27] The communists proposed removing Chiang's power.[34] When Chiang gradually gained the support of Western countries, the conflict between him and the communists became more and more intense. Chiang asked the Kuomintang to join the Comintern to rule out the secret expansion of communists within the KMT, while Chen Duxiu hoped that the communists would completely withdraw from the KMT.[35]""",
    ]
    args = parse_args()
    with open(args.input_file) as f:
        for line in f:
            d = json.loads(line)
            prompt = d["body"]["messages"][1]["content"]
            # prompt = template.format(text=psg,number=random.choices([2,3,4,5,6,7,8,9,10])[0])
            print(prompt)
            try:
                response = generate_text_with_qwen(prompt, max_length=500, temperature=0.7)
                print(f"\nPrompt: {prompt}")
                print(f"\nResponse: {response}")
                print("\n\n%%%%%%\n\n")
                
            except Exception as e:
                print(f"Error: {e}")
                print("\nNote: This model requires significant GPU memory (32GB+ recommended)")
                print("Consider using quantized versions or smaller models if you have limited resources")

# # Alternative: Using transformers pipeline (simpler but less control)
# def simple_qwen_generation(prompt):
#     """
#     Simplified text generation using transformers pipeline
#     """
#     from transformers import pipeline
    
#     pipe = pipeline(
#         "text-generation",
#         model="Qwen/Qwen2.5-32B-Instruct",
#         torch_dtype=torch.float16,
#         device_map="auto"
#     )
    
#     messages = [
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": prompt}
#     ]
    
#     response = pipe(messages, max_new_tokens=256, temperature=0.7)
#     return response[0]['generated_text'][-1]['content']
