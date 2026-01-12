import os
import sys
from pathlib import Path

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
        "C++": ["Java", "Python", "Rust", "Go", "JavaScript"],
        "Java": ["C++", "Python", "Rust", "Go", "JavaScript"],
        "Python": ["C++", "Java", "Rust", "Go", "JavaScript"],
        "Rust": ["C++", "Java", "Python", "Go", "JavaScript"],
        "Go": ["C++", "Java", "Python", "Rust", "JavaScript"],
        "JavaScript": ["C++", "Java", "Python", "Rust", "Go"],
    },
    "evalplus": {
        "Python": ["Java"],
    },
}
DATASET_INSTANCES = { "codenet": 200, "avatar": 240, "codenetintertrans": 35, "evalplus": 164, }

# =========================
# Placeholder (replace with your real function)
# =========================

def get_score_lang_pair(model, trans_type, dataset, src_lang):
    return "1.00"
    total_per_lang = DATASET_INSTANCES[dataset]
    n_tl = 0
    total_corrects = 0
    for tl in LANG_MAP[dataset][src_lang]:
        file_path = f"Repair/{model}/{trans_type}/itr3/Reports/{dataset}/{src_lang}/{tl}/{dataset}_compileReport_from_{src_lang}_to_{tl}.txt"
        if os.path.exists(file_path):
            n_tl += 1
            with open(file_path, "r") as f:
                lines = [l.strip() for l in f.readlines()]                        
                for l in lines:
                  if l.startswith("Total Instances:"):
                    incorrects = int(l.split(":")[-1].strip())
                  elif l.startswith("Total Correct:"):
                    corrects = int(l.split(":")[-1].strip())
                total_corrects += (total - incorrects + corrects)
        else:
            print("file not found", file_path)
    return round(100 * total_corrects/(n_tl*total_per_lang), 2)
            
# =========================
# LaTeX row generator
# =========================

def print_latex_row(dataset, src_lang, tgt_langs):
    cells = []

    # Dataset / Source / Targets
    cells.append(dataset.capitalize() if dataset else "")
    cells.append(src_lang)
    cells.append(", ".join(tgt_langs))

    # Model × Prompt source results
    for model in MODELS:
        for trans in TRANS_TYPES:
            try:
                score = get_score_lang_pair(
                    model=model,
                    trans_type=trans,
                    dataset=dataset,
                    src_lang=src_lang,
                )
                cells.append(f"{score:.2f}")
            except Exception as e:
                print(f"\n{str(e)}\n")
                cells.append("--")

    print(" & ".join(cells) + r" \\")


# =========================
# Main: emit table body
# =========================

def print_latex_table_body():
    for dataset in DATASETS:
        first_row = True

        for src_lang, tgt_langs in LANG_MAP[dataset].items():
            if first_row:
                print_latex_row(dataset, src_lang, tgt_langs)
                first_row = False
            else:
                # Empty dataset cell for visual grouping
                print_latex_row("", src_lang, tgt_langs)

        print(r"\midrule")


if __name__ == "__main__":
    print_latex_table_body()
