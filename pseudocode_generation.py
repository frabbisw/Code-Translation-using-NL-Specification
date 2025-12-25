import os
import logging
from dotenv import load_dotenv
from local_model import LocalCausalLMRunner
import OpenAICall

os.makedirs(f'logs', exist_ok=True)
logging.basicConfig(filename=f"logs/pseudocode_generation.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def generate_translation_from_pseudocode(content, to):
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": content}]
    response = OpenAICall.send_message_to_openai(message)
    return response.replace("cpp\n", "").replace(f"```{to.lower()}", "").replace("```", "")

def generate_pseudocode_from_source(content, source, model):
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": content}]
    if isinstance(model, str) and "gpt" in model:
        print(f"model {model} is selected. fetching response using api ...")
        response = OpenAICall.send_message_to_openai(message).replace("```", "")
    elif isinstance(model, LocalCausalLMRunner):
        print(f"model {model.model_name} is selected. running locally ...")
        response = model.run(message)
    return response

def pseudocode_generation(dataset, source, filename, model):
    content_dir = f"dataset/{dataset}/{source}/Code/{filename}"

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
        pseudocode_file_dir = f"Generations/Pseudocodes/{dataset}/{source}"
        os.makedirs(pseudocode_file_dir, exist_ok=True)

        with open(pseudocode_file, "w") as pseudocode_fp:
            pseudocode_fp.write(pseudocode_response)
            pseudocode_fp.close()

# if __name__ == "__main__":
#     load_dotenv()
#     parser = argparse.ArgumentParser(description='run pseudocode generation with a given model, dataset and languages')
#     parser.add_argument('--dataset', help='dataset to use for pseudocode generation. should be one of [codenet,avatar]', required=True, type=str)
#     parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
#     parser.add_argument('--filename', help='path to source code', required=True, type=str)
#     parser.add_argument('--model', help='model to use for code translation.', required=True, type=str)
#     parser.add_argument('--models_dir', help='directory where the models are kept.', required = True, type=str)
    
#     args = parser.parse_args()

#     source = args.source_lang
#     dataset = args.dataset
#     filename = args.filename
#     content_dir = f"dataset/{dataset}/{source}/Code/{filename}"
#     content =""

#     with open(content_dir, "r") as content_file:
#         content = content_file.read()
#         content_file.close()

#     skip = False
#     base_filename = filename.split(".")[0]
#     pseudocode_file = f"Generations/Pseudocodes/{dataset}/{source}/{base_filename}.txt"
#     if os.path.exists(pseudocode_file):
#         skip = True

#     if not skip:
#         message = f"{content}\n\nGive pseudocode for the above {source} code so that the {source} code is reproducible from the pseudocode. Do not give any other explanation except the pseudocode."
        
#         model = args.model
#         model_map = {"magicoder": "Magicoder-S-DS-6.7B", "starcoder": "starcoder2-15b"}
#         if model in ["starcoder", "magicoder"]:
#             models_dir = args.models_dir
#             model = LocalCausalLMRunner(f"{models_dir}/{model_map[model]}")
        
#         pseudocode_response = generate_pseudocode_from_source(message, source, model)

#         pseudocode_file_dir = f"Generations/Pseudocodes/{dataset}/{source}"
#         os.makedirs(pseudocode_file_dir, exist_ok=True)

#         with open(pseudocode_file, "w") as pseudocode_fp:
#             pseudocode_fp.write(pseudocode_response)
#             pseudocode_fp.close()

#     skip = False
#     src_regen_file = f"Generations/source_regeneration/{dataset}/{source}/{filename}"
#     if os.path.exists(src_regen_file):
#         skip = True

#     if not skip:
#         message = f"{pseudocode_response}\n\nThe above pseudocode was generated from {source}. Regenerate the {source} code from the pseudocode. Print only the {source} code and end with the comment \"End of Code\". Do not give any other explanation."

#         source_response = generate_translation_from_pseudocode(message, source)

#         src_regen_file_dir = f"Generations/source_regeneration/{dataset}/{source}"
#         os.makedirs(src_regen_file_dir, exist_ok=True)

#         with open(src_regen_file, "w") as source_regen_fp:
#             source_regen_fp.write(source_response)
#             source_regen_fp.close()
