import os
import sys
from pathlib import Path
import pdb
import josn
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
        "C++": ["Java", "Python", "Rust", "Go", "Javascript"],
        "Java": ["C++", "Python", "Rust", "Go", "Javascript"],
        "Python": ["C++", "Java", "Rust", "Go", "Javascript"],
        "Rust": ["C++", "Java", "Python", "Go", "Javascript"],
        "Go": ["C++", "Java", "Python", "Rust", "Javascript"],
        "Javascript": ["C++", "Java", "Python", "Rust", "Go"],
    },
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
                            with open(os.path.join(project_path, "sonar_report", filename), "r") as f:
                                contents = json.load(f)
                                try:
                                    sonar_values[key] = 1000 * (contents["severity"]["CRITICAL"] if "CRITICAL" in contents["severity"] else 0 + contents["severity"]["BLOCKER"] if "BLOCKER" in contents["severity"] else 0) / contents["ncloc"]
                                except:
                                    sonar_values[key] = 0


def get_cell_value(model, dataset, src, tgt, mode):
    pass

def generate_table_rows():
    rows = []

    for dataset in DATASETS:
        lang_pairs = LANG_MAP[dataset]

        for src_lang, tgt_langs in lang_pairs.items():
            for tgt_lang in tgt_langs:
                row = []

                # First three columns
                row.append(dataset)
                row.append(src_lang)
                row.append(tgt_lang)

                # Model columns: GPT-4, Magicoder, DeepSeek
                for model in MODELS:
                    for trans_type in TRANS_TYPES:
                        mode = MODE_MAP[trans_type]
                        value = get_cell_value(
                            model=model,
                            dataset=dataset,
                            src=src_lang,
                            tgt=tgt_lang,
                            mode=mode,
                        )
                        row.append(str(value))

                # Convert to LaTeX row
                latex_row = " & ".join(row) + r" \\"
                print(latex_row)

# Example usage
if __name__ == "__main__":
    project_path = Path.cwd().parent
    prepare_sonar_dict("codenl", project_path)
    print(sonar_values)
    # generate_table_rows()
    


