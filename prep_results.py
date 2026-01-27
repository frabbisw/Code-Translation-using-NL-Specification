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
    # "codenetintertrans": {
    #     "C++": ["Java", "Python", "Go"],
    #     "Java": ["C++", "Python", "Go"],
    #     "Python": ["C++", "Java", "Go"],
    #     "Go": ["C++", "Java", "Python"],
    #     "Rust": ["C", "C++", "Java", "Python"],
    #     "Javascript": ["C", "C++", "Java", "Python"],
    # },
    "evalplus": {
        "Python": ["Java"],
    },
}
DATASET_INSTANCES = { "codenet": 200, "avatar": 240, "codenetintertrans": 35, "evalplus": 164}

def get_file_path(model, trans_type, dataset, src_lang, tl):
    path3 = f"Repair/{model}/{trans_type}/itr3/Reports/{dataset}/{src_lang}/{tl}/{dataset}_compileReport_from_{src_lang}_to_{tl}.txt"
    path2 = f"Repair/{model}/{trans_type}/itr2/Reports/{dataset}/{src_lang}/{tl}/{dataset}_compileReport_from_{src_lang}_to_{tl}.txt"
    path1 = f"Repair/{model}/{trans_type}/itr1/Reports/{dataset}/{src_lang}/{tl}/{dataset}_compileReport_from_{src_lang}_to_{tl}.txt"
    path0 = f"Generations/{model}/{trans_type}/Reports/{dataset}/{src_lang}/{tl}/{dataset}_compileReport_from_{src_lang}_to_{tl}.txt"

    for path in [path3, path2, path1, path0]:
        if os.path.exists(path):
            return path
    return None

def get_score_lang_pair(model, trans_type, dataset, src_lang):
    total_per_lang = DATASET_INSTANCES[dataset]
    n_tl = 0
    total_corrects = 0
    for tl in LANG_MAP[dataset][src_lang]:
        file_path = get_file_path(model, trans_type, dataset, src_lang, tl)
        if file_path is not None:
            n_tl += 1
            with open(file_path, "r") as f:
                lines = [l.strip() for l in f.readlines()]                        
                for l in lines:
                  if l.startswith("Total Instances:"):
                    incorrects = int(l.split(":")[-1].strip())
                  elif l.startswith("Total Correct:"):
                    corrects = int(l.split(":")[-1].strip())
                total_corrects += (total_per_lang - incorrects + corrects)
        else:
            # print("file not found", file_path)
            continue
    if n_tl < 1:
        return "-1"
    return round(100 * total_corrects/(n_tl*total_per_lang), 2)
            

# print(get_score_lang_pair("magicoder", "translation_source", "codenet", "Python"))

# pdb.set_trace()


# exit(0)

def print_latex_row(dataset_key, dataset_cell, src_lang, tgt_langs):
    # print("print_latex_row")
    cells = []

    # Printed columns
    cells.append(dataset_cell)
    cells.append(src_lang)
    # cells.append(", ".join(tgt_langs))

    # Model × Prompt source results
    for model in MODELS:
        for trans in TRANS_TYPES:
            try:
                score = get_score_lang_pair(
                    model=model,
                    trans_type=trans,
                    dataset=dataset_key,   # ALWAYS valid
                    src_lang=src_lang,
                )
                cells.append(f"{score:.2f}")
            except Exception:
                cells.append("-")

    print(" & ".join(cells) + r" \\")


def print_latex_table_body():
    print("print_latex_table_body")
    for dataset in DATASETS:
        first_row = True

        for src_lang, tgt_langs in LANG_MAP[dataset].items():
            if first_row:
                dataset_cell = dataset.capitalize()
                first_row = False
            else:
                dataset_cell = ""   # visual grouping only

            print_latex_row(
                dataset_key=dataset,
                dataset_cell=dataset_cell,
                src_lang=src_lang,
                tgt_langs=tgt_langs,
            )

        print(r"\hline")


if __name__ == "__main__":
    print_latex_table_body()
