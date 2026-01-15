import os
import logging
import re
from local_model import LocalCausalLMRunner
import OpenAICall
import utility

os.makedirs(f'logs', exist_ok=True)
logging.basicConfig(filename=f"logs/translation_generation_source.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def generate_translation_from_source(content, to, model):
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": content}]

    if isinstance(model, str) and "gpt" in model:
        print(f"model {model} is selected. fetching response using api ...")
        response = OpenAICall.send_message_to_openai(message, model)
    elif isinstance(model, str) and "deepseek" in model:
        print(f"model {model} is selected. fetching response using api ...")
        response = OpenAICall.send_message_to_deepseek(message)
    elif isinstance(model, LocalCausalLMRunner):
        print(f"model {model.model_name} is selected. running locally ...")
        response = model.run(message)
    return response.replace("cpp\n", "").replace(f"```{to.lower()}", "").replace("```", "")

def translation_generation_sc(dataset, source, target, filename, model, model_name):
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
    elif target == "Javascript":
        file_ext = "js"
    elif target == "Rust":
        file_ext = "rs"    
    
    content_dir = f"dataset/{dataset}/{source}/Code/{filename}"
    content =""

    with open(content_dir, "r") as content_file:
        content = content_file.read()
        content_file.close()

    skip = False
    target_file = f"Generations/{model_name}/translation_source/{dataset}/{source}/{target}/{file_basename}.{file_ext}"
    if os.path.exists(target_file):
        skip = True

    if not skip:
        message = f"{content}\n\nThis is a {source} code. Generate functionally correct and similar {target} code using the from the {source} code. Print only the {target} code and end with the comment \"End of Code\". Do not give any other explanation."
        
        target_response = generate_translation_from_source(message, target, model)

        target_response = re.sub('public\s*class\s*.+', 'public class ' + file_basename + ' {', target_response)

        target_response = utility.normalize_java_util(target_response)

        target_response, _ = utility.remove_Tuple_class(utility.get_longest_code_snippet(target_response), file_basename)

        target_file_dir = f"Generations/{model_name}/translation_source/{dataset}/{source}/{target}"
        os.makedirs(target_file_dir, exist_ok=True)

        with open(target_file, "w") as target_fp:
            target_fp.write(target_response)
            target_fp.close()
    

# if __name__ == "__main__":
#     load_dotenv()
#     parser = argparse.ArgumentParser(description='run translation with GPT-4 with a given dataset and languages')
#     parser.add_argument('--dataset', help='dataset to use for code translation. should be one of [codenet,avatar]', required=True, type=str)
#     parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
#     parser.add_argument('--target_lang', help='target language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
#     parser.add_argument('--filename', help='path to source code', required=True, type=str)
#     parser.add_argument('--model', help='model to use for code translation.', required=True, type=str)
#     parser.add_argument('--models_dir', help='directory where the models are kept.', required = True, type=str)
#     args = parser.parse_args()

#     source = args.source_lang
#     target = args.target_lang
#     dataset = args.dataset
#     filename = args.filename

#     if source == target:
#         exit()
    
#     file_basename = filename.split(".")[0]
#     file_ext = "c"
#     if target == "Java":
#         file_ext = "java"
#     elif target == "Python":
#         file_ext = "py"
#     elif target == "Go":
#         file_ext = "go"
#     elif target == "C++":
#         file_ext = "cpp"
    
#     content_dir = f"dataset/{dataset}/{source}/Code/{filename}"
#     # pseudocode_dir = f"Generations/Pseudocodes/{dataset}/{source}/{file_basename}.txt"
#     content =""
#     # pseudocode_content = ""

#     with open(content_dir, "r") as content_file:
#         content = content_file.read()
#         content_file.close()
    
#     # with open(pseudocode_dir, "r") as pseudocode_file:
#     #     pseudocode_content = pseudocode_file.read()
#     #     pseudocode_file.close()

    
#     skip = False
#     target_file = f"Generations/translation_source/{dataset}/{source}/{target}/{file_basename}.{file_ext}"
#     if os.path.exists(target_file):
#         skip = True

#     if not skip:
#         message = f"{content}\n\nThis is a {source} code. Generate functionally correct and similar {target} code using the from the {source} code. Print only the {target} code and end with the comment \"End of Code\". Do not give any other explanation."
        
#         model = args.model
#         model_map = {"magicoder": "Magicoder-S-DS-6.7B", "starcoder": "starcoder2-15b"}
#         if model in ["starcoder", "magicoder"]:
#             models_dir = args.models_dir
#             model = LocalCausalLMRunner(f"{models_dir}/{model_map[model]}")
#         target_response = generate_translation_from_source(message, target, model)

#         if dataset == "evalplus":
#             target_response = "package com.example;\n" + target_response

#         target_response = re.sub('public\s*class\s*.+', 'public class ' + file_basename + ' {', target_response)

#         target_file_dir = f"Generations/translation_source/{dataset}/{source}/{target}"
#         os.makedirs(target_file_dir, exist_ok=True)

#         with open(target_file, "w") as target_fp:
#             target_fp.write(target_response)
#             target_fp.close()
