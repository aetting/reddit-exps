from transformers import AutoModelForCausalLM, AutoTokenizer
device = "cuda" # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-7B-Instruct", device_map="auto")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-7B-Instruct")

prompt = """
"step 1 question why is air under the diaphragm called pneumoperitoneum? how is the air in peritoneum if the air is under diaphragm? The diaphragm separates the thorax and abdomen. Therefore if air is under the diaphragm, it\u2019s in the peritoneal cavity."

Please take information from this text and create three multiple choice questions that use 2-4 blanks. Example:

"Dogs are ___ with ___ legs and ___ tail."
A. mammals; four; one
B. mammals; two; one
C. amphibians; two; one
D. amphibians; four; two

Answer: B
"""

messages = [{"role": "user", "content": prompt}]

text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

model_inputs = tokenizer([text], return_tensors="pt").to(device)

generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=512, do_sample=True)

generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print(response)

with open("/output/output.json","w") as out:
    out.write(response + "\n")