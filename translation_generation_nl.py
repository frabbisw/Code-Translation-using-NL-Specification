import os
import openai
from openai import OpenAI
import logging
import tiktoken
from dotenv import load_dotenv
import argparse
import re
from local_model import LocalCausalLMRunner

os.makedirs(f'logs', exist_ok=True)
logging.basicConfig(filename=f"logs/translation_generation_nl.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def send_message_to_openai(message_log):
    "Use OpenAI's ChatCompletion API to get the chatbot's response"
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    num_tokens = len(encoding.encode(message_log[1]["content"]))

    response = "exceptional case"
    is_success = False
    max_attempts = 5
    client = OpenAI()
    while max_attempts > 0:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # The name of the OpenAI chatbot model to use
                # The conversation history up to this point, as a list of dictionaries
                messages=message_log,
                # The maximum number of tokens (words or subwords) in the generated response
                max_tokens=max(1, 8000-num_tokens),
                # The "creativity" of the generated response (higher temperature = more creative)
                temperature=0.7,
            )
            is_success = True
            break
        except openai.error.InvalidRequestError as e:
            return "# Token size exceeded."
        except:
            max_attempts -= 1
            continue

    if not is_success:
        return response

    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response.choices[0].message.content

def generate_translation_from_pseudocode(content, to, model):
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": content}]
    response = send_message_to_openai(message)

    if isinstance(model, str) and "gpt" in model:
        print(f"model {model} is selected. fetching response using api ...")
        response = send_message_to_openai(message)
    elif isinstance(model, LocalCausalLMRunner):
        print(f"model {model.model_name} is selected. running locally ...")
        response = model.run(message)

    return response.replace("cpp\n", "").replace(f"```{to.lower()}", "").replace("```", "")


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description='run translation with GPT-4 with a given dataset and languages')
    parser.add_argument('--dataset', help='dataset to use for code translation. should be one of [codenet,avatar]', required=True, type=str)
    parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--target_lang', help='target language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--filename', help='path to source code', required=True, type=str)
    parser.add_argument('--model', help='model to use for code translation.', required=True, type=str)
    parser.add_argument('--models_dir', help='directory where the models are kept.', required = True, type=str)
    args = parser.parse_args()

    source = args.source_lang
    target = args.target_lang
    dataset = args.dataset
    filename = args.filename

    if source == target:
        exit()
    
    file_basename = filename.split(".")[0]
    file_ext = "c"
    if target == "Java":
        file_ext = "java"
    elif target == "Python":
        file_ext = "py"
    elif target == "Go":
        file_ext = "go"
    elif target == "C++":
        file_ext = "cpp"
    
    content_dir = f"dataset/{dataset}/{source}/Code/{filename}"
    pseudocode_dir = f"Generations/Pseudocodes/{dataset}/{source}/{file_basename}.txt"
    content =""
    pseudocode_content = ""

    with open(content_dir, "r") as content_file:
        content = content_file.read()
        content_file.close()
    
    with open(pseudocode_dir, "r") as pseudocode_file:
        pseudocode_content = pseudocode_file.read()
        pseudocode_file.close()

    
    skip = False
    target_file = f"Generations/translation_nl/{dataset}/{source}/{target}/{file_basename}.{file_ext}"
    if os.path.exists(target_file):
        skip = True

    if not skip:
        message = f"{pseudocode_content}\n\nThe above pseudocode was generated from {source}. Generate functionally correct and similar {target} code using the pseudocode. Print only the {target} code and end with the comment \"End of Code\". Do not give any other explanation."

        model = args.model
        model_map = {"magicoder": "Magicoder-S-DS-6.7B", "starcoder": "starcoder2-15b"}
        if model in ["starcoder", "magicoder"]:
            models_dir = args.models_dir
            model = LocalCausalLMRunner(f"{models_dir}/{model_map[model]}")

        target_response = generate_translation_from_pseudocode(message, target, model)

        if dataset == "evalplus":
            target_response = "package com.example;\n" + target_response

        target_response = re.sub('public\s*class\s*.+', 'public class ' + file_basename + ' {', target_response)

        target_file_dir = f"Generations/translation_nl/{dataset}/{source}/{target}"
        os.makedirs(target_file_dir, exist_ok=True)

        with open(target_file, "w") as target_fp:
            target_fp.write(target_response)
            target_fp.close()
