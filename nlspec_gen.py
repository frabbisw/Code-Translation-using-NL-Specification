import os
import openai
from openai import OpenAI
import logging
import tiktoken
from dotenv import load_dotenv
import argparse
from local_model import LocalCausalLMRunner
import pdb

os.makedirs(f'logs', exist_ok=True)
logging.basicConfig(filename=f"logs/pseudocode_generation.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def send_message_to_openai(message_log):
    "Use OpenAI's ChatCompletion API to get the chatbot's response"
    encoding = tiktoken.encoding_for_model("gpt-4")
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

def generate_translation_from_pseudocode(content, to):
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": content}]
    response = send_message_to_openai(message)
    return response.replace("cpp\n", "").replace(f"```{to.lower()}", "").replace("```", "")

def generate_pseudocode_from_source(content, source, model):
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": content}]
    if isinstance(model, str) and "gpt" in model:
        print(f"model {model} is selected. fetching response using api ...")
        response = send_message_to_openai(message).replace("```", "")
    elif isinstance(model, LocalCausalLMRunner):
        print(f"model {model.model_name} is selected. running locally ...")
        response = model.run(message)
    return response

def run_by_file(dataset, source_lang, filename, model, models_dir):
    content_dir = f"dataset/{dataset}/{source}/Code/{filename}"
    content =""

    with open(content_dir, "r") as content_file:
        content = content_file.read()
        content_file.close()

    skip = False
    base_filename = filename.split(".")[0]
    pseudocode_file = f"Generations/Pseudocodes/{dataset}/{source}/{base_filename}.txt"
    if os.path.exists(pseudocode_file):
        skip = True

    if not skip:
        message = f"{content}\n\nGive pseudocode for the above {source} code so that the {source} code is reproducible from the pseudocode. Do not give any other explanation except the pseudocode."
                
        pseudocode_response = generate_pseudocode_from_source(message, source, model)
        pdb.set_trace()
        
        pseudocode_file_dir = f"Generations/Pseudocodes/{dataset}/{source}"
        os.makedirs(pseudocode_file_dir, exist_ok=True)

        with open(pseudocode_file, "w") as pseudocode_fp:
            pseudocode_fp.write(pseudocode_response)
            pseudocode_fp.close()

