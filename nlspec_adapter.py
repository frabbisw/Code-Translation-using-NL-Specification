import os
from pseudocode_generation import run_by_file
import openai
from openai import OpenAI
import logging
import tiktoken
from dotenv import load_dotenv
import sys

LANGUAGES = {
    "Python": "py",
    "Java": "java",
    "C++": "cpp",
    "C": "c",
    "Go": "go",
}

def pseudocode_generation(dataset, source_lang, filename, model, models_dir):
    print(
        f"Generating Pseudocode of {source_lang} "
        f"in dataset {dataset} using model {model}..."
    )
    run_by_file(dataset, source_lang, filename, model, models_dir)


def file_looper(model, model_dir, src_dataset, src_lang):
    if src_lang not in LANGUAGES:
        raise ValueError(f"Unsupported source language: {src_lang}")

    ext = LANGUAGES[src_lang]
    code_dir = f"dataset/{src_dataset}/{src_lang}/Code"

    if not os.path.isdir(code_dir):
        raise FileNotFoundError(f"Directory not found: {code_dir}")

    for file in os.listdir(code_dir):
        if file.endswith(f".{ext}"):
            # Keep filename exactly as the bash version:
            # basename + .ext
            base_name = file
            pseudocode_generation(
                src_dataset,
                src_lang,
                base_name,
                model,
                model_dir,
            )


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python run_pseudocode_generation.py "
            "<model> <model_dir> <src_dataset> <src_lang>"
        )
        sys.exit(1)

    model = sys.argv[1]
    model_dir = sys.argv[2]
    src_dataset = sys.argv[3]
    src_lang = sys.argv[4]

    model_map = {"magicoder": "Magicoder-S-DS-6.7B", "starcoder": "starcoder2-15b"}
    if model in ["starcoder", "magicoder"]:
        model = LocalCausalLMRunner(f"{models_dir}/{model_map[model]}")
    else:
        load_dotenv()
    
    file_looper(model, model_dir, src_dataset, src_lang)

