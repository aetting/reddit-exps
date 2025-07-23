from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

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
    
    # Load model and tokenizer
    model_name = "Qwen/Qwen2.5-32B-Instruct"
    
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,  # Use half precision to save memory
        device_map="auto",          # Automatically distribute across available GPUs
        trust_remote_code=True
    )
    
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

# Example usage
if __name__ == "__main__":
    prompt = "Explain the concept of machine learning in simple terms."
    
    try:
        response = generate_text_with_qwen(prompt, max_length=256, temperature=0.7)
        print(f"\nPrompt: {prompt}")
        print(f"\nResponse: {response}")
        
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
