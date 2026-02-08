import os
import sys
from pathlib import Path
import pdb

# =========================
# Configuration
# =========================

MODELS = ["gpt4", "magicoder", "deepseek"]

TRANS_TYPES = [
    "translation_nl",
    "translation_source",
    "translation_nl_and_source",
]

DATASETS = [
    "avatar",
    "codenet",
    "codenetintertrans",
    "evalplus",
]

LANG_MAP = {
    "codenet": {
        "Python": ["C", "C++", "Java", "Go"],
        "Java": ["C", "C++", "Python", "Go"],
        "C": ["C++", "Java", "Python", "Go"],
        "C++": ["C", "Java", "Python", "Go"],
        "Go": ["C", "C++", "Java", "Python"],
    },
    "avatar": {
        "Python": ["Java"],
        "Java": ["Python"],
    },
    "codenetintertrans": {
        "C++": ["Java", "Python", "Rust", "Go", "Javascript"],
        "Java": ["C++", "Python", "Rust", "Go", "Javascript"],
        "Python": ["C++", "Java", "Rust", "Go", "Javascript"],
        "Rust": ["C++", "Java", "Python", "Go", "Javascript"],
        "Go": ["C++", "Java", "Python", "Rust", "Javascript"],
        "Javascript": ["C++", "Java", "Python", "Rust", "Go"],
    },
    "codenetintertrans": {
        "C++": ["Java", "Python", "Go"],
        "Java": ["C++", "Python", "Go"],
        "Python": ["C++", "Java", "Go"],
        "Go": ["C++", "Java", "Python"],
        "Rust": ["C", "C++", "Java", "Python"],
        "Javascript": ["C", "C++", "Java", "Python"],
    },
    "evalplus": {
        "Python": ["Java"],
    },
}
DATASET_INSTANCES = { "codenet": 200, "avatar": 240, "codenetintertrans": 35, "evalplus": 164}

def get_file_path_fixed(model, trans_type, dataset, src_lang, tl):
    path3 = f"Repair/{model}/{trans_type}/itr3/Reports/{dataset}/{src_lang}/{tl}/{dataset}_compileReport_from_{src_lang}_to_{tl}.txt"
    path2 = f"Repair/{model}/{trans_type}/itr2/Reports/{dataset}/{src_lang}/{tl}/{dataset}_compileReport_from_{src_lang}_to_{tl}.txt"
    path1 = f"Repair/{model}/{trans_type}/itr1/Reports/{dataset}/{src_lang}/{tl}/{dataset}_compileReport_from_{src_lang}_to_{tl}.txt"
    path0 = f"Generations/{model}/{trans_type}/Reports/{dataset}/{src_lang}/{tl}/{dataset}_compileReport_from_{src_lang}_to_{tl}.txt"

    for path in [path3, path2, path1, path0]:
        if os.path.exists(path):
            return path
    return None

def get_file_path_trans(model, trans_type, dataset, src_lang, tl):
    path0 = f"Generations/{model}/{trans_type}/Reports/{dataset}/{src_lang}/{tl}/{dataset}_compileReport_from_{src_lang}_to_{tl}.txt"
    if os.path.exists(path0):
        return path
    return None

def count_corrects(file_path):
    with open(file_path, "r") as f:
        lines = [l.strip() for l in f.readlines()]                        
        for l in lines:
          if l.startswith("Total Instances:"):
            incorrects = int(l.split(":")[-1].strip())
          elif l.startswith("Total Correct:"):
            corrects = int(l.split(":")[-1].strip())
        print(file_path, total_per_lang - incorrects + corrects)
        return (total_per_lang - incorrects + corrects)        

def get_score_lang_pair(model, trans_type, dataset, src_lang):
    total_per_lang = DATASET_INSTANCES[dataset]
    n_tl = 0
    total_corrects_fixed = 0
    total_corrects_trans = 0
    
    for tl in LANG_MAP[dataset][src_lang]:
        file_path_fixed = get_file_path_fixed(model, trans_type, dataset, src_lang, tl)
        file_path_trans = get_file_path_trans(model, trans_type, dataset, src_lang, tl)
        if file_path_fixed is not None:
            n_tl += 1
            total_corrects_fixed += count_corrects_fixed(file_path_fixed)
            total_corrects_trans += count_corrects_trans(file_path_trans)
        else:
            print("file not found", file_path)
            continue
    
    if n_tl < 1:
        return "-1"
    print(total_corrects_fixed, total_corrects_trans)
    fixed_score = round(100 * total_corrects_fixed/(n_tl*total_per_lang), 2)
    trans_score = round(100 * total_corrects_trans/(n_tl*total_per_lang), 2)
    return f"{fixed_score}//% {trans_score}\\%$\\uparrow$"
            

# print(get_score_lang_pair("magicoder", "translation_source", "codenet", "Python"))

# pdb.set_trace()


# exit(0)

def print_latex_row(model, dataset, src_lang):
    print(model, dataset, src_lang, end=" || ")
    for trans_type in TRANS_TYPES:
        cell = get_score_lang_pair(model, trans_type, dataset, src_lang)
        print(cell, end=" & ")
    print("\\\\")
    
def print_model(model):
    for dataset in DATASETS:
        for src_lang, tgt_langs in LANG_MAP[dataset].items():
            print_latex_row(model, dataset, src_lang)
                
print_model("magicoder")
print("="*50)
print_model("deepseek")
