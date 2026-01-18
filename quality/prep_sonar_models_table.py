import os
import sys
from pathlib import Path
import pdb
import json
from pathlib import Path

# =========================
# Configuration
# =========================

MODELS = ["gpt4", "magicoder", "deepseek"]
# MODELS = ["deepseek", "gpt4", "magicoder"]

TRANS_TYPES = [
    "translation_nl",
    "translation_source",
    "translation_nl_and_source",
]

DATASETS = [
    "avatar",
    "codenet",
    # "codenetintertrans",
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
        "Python": ["Java", "C", "C++", "Go"],
        "Java": ["Python", "C", "C++", "Go"],
    },
    # "codenetintertrans": {
    #     "C++": ["Java", "Python", "Rust", "Go", "Javascript"],
    #     "Java": ["C++", "Python", "Rust", "Go", "Javascript"],
    #     "Python": ["C++", "Java", "Rust", "Go", "Javascript"],
    #     "Rust": ["C++", "Java", "Python", "Go", "Javascript"],
    #     "Go": ["C++", "Java", "Python", "Rust", "Javascript"],
    #     "Javascript": ["C++", "Java", "Python", "Rust", "Go"],
    # },
    "evalplus": {
        "Python": ["Java"],
    },
}

# Mapping from TRANS_TYPES to table modes
MODE_MAP = {
    "translation_nl": "N",
    "translation_source": "S",
    "translation_nl_and_source": "N+S",
}

lang_id_map = {
    "C++": "cpp",
    "Java": "java",
    "Go": "go",
    "C": "c",
    "Python": "py",
    "Javascript": "js",
    "Rust": "rs",
}

sonar_values = {}

def prepare_sonar_dict(org_name, project_path):
    for model in MODELS:
        for dataset in LANG_MAP.keys():
            for src in LANG_MAP[dataset].keys():
                for tgt in LANG_MAP[dataset][src]:
                    for mode in MODE_MAP.keys():
                        key = f"{model}_{dataset}_{src}_{tgt}_{mode}"
                        print(key)
                        filepath = os.path.join(project_path, "sonar_report", f"{org_name}_{model}_{dataset}_{lang_id_map[src]}_{lang_id_map[tgt]}_{mode}_Repair_summary.json")
                        if not os.path.exists(filepath):
                            sonar_values[key] = "-"
                        else:
                            with open(os.path.join(project_path, "sonar_report", filepath), "r") as f:
                                contents = json.load(f)
                                try:
                                    critical = contents["severity"].get("CRITICAL", 0)
                                    blocker = contents["severity"].get("BLOCKER", 0)
                                    sonar_values[key] = round(1000 * (critical + blocker) / int(contents["ncloc"]), 2)                                    
                                except Exception as e:
                                    sonar_values[key] = 0

def get_cell_value(model, dataset, src, tgt, mode):
    key = f"{model}_{dataset}_{src}_{tgt}_{mode}"
    return sonar_values[key]

def generate_table_rows():
    for dataset in DATASETS:
        lang_pairs = LANG_MAP[dataset]
        seen_pairs = set()  # <-- key fix

        for src_lang, tgt_langs in lang_pairs.items():
            for tgt_lang in tgt_langs:
                pair_key = (src_lang, tgt_lang)

                # Skip duplicates
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                row = []

                # First three columns
                row.append(dataset)
                row.append(src_lang)
                row.append(tgt_lang)

                # Model columns: GPT-4, Magicoder, DeepSeek
                for model in MODELS:
                    for trans_type in TRANS_TYPES:
                        value = get_cell_value(
                            model=model,
                            dataset=dataset,
                            src=src_lang,
                            tgt=tgt_lang,
                            mode=trans_type,
                        )
                        row.append(str(value) if value is not None else "-")

                latex_row = " & ".join(row) + r" \\"
                print(latex_row)

# Example usage
if __name__ == "__main__":
    project_path = Path.cwd().parent
    prepare_sonar_dict("codenl", project_path)
    print("values are ready. preparing table ...")
    print("="*50)
    # print(sonar_values)
    generate_table_rows()
    


