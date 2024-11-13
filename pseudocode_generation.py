import os
import openai
from openai import OpenAI
import logging
import tiktoken
from dotenv import load_dotenv
import argparse

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
                model="gpt-4",  # The name of the OpenAI chatbot model to use
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

def generate_pseudocode_from_source(content, source):
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": content}]
    response = send_message_to_openai(message).replace("```", "")
    return response

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description='run pseudocode generation with a given model, dataset and languages')
    parser.add_argument('--dataset', help='dataset to use for pseudocode generation. should be one of [codenet,avatar]', required=True, type=str)
    parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--filename', help='path to source code', required=True, type=str)
    args = parser.parse_args()

    source = args.source_lang
    dataset = args.dataset
    filename = args.filename
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

        pseudocode_response = generate_pseudocode_from_source(message, source)

        pseudocode_file_dir = f"Generations/Pseudocodes/{dataset}/{source}"
        os.makedirs(pseudocode_file_dir, exist_ok=True)

        with open(pseudocode_file, "w") as pseudocode_fp:
            pseudocode_fp.write(pseudocode_response)
            pseudocode_fp.close()

    skip = False
    src_regen_file = f"Generations/source_regeneration/{dataset}/{source}/{filename}"
    if os.path.exists(src_regen_file):
        skip = True

    if not skip:
        message = f"{pseudocode_response}\n\nThe above pseudocode was generated from {source}. Regenerate the {source} code from the pseudocode. Print only the {source} code and end with the comment \"End of Code\". Do not give any other explanation."

        source_response = generate_translation_from_pseudocode(message, source)

        src_regen_file_dir = f"Generations/source_regeneration/{dataset}/{source}"
        os.makedirs(src_regen_file_dir, exist_ok=True)

        with open(src_regen_file, "w") as source_regen_fp:
            source_regen_fp.write(source_response)
            source_regen_fp.close()
