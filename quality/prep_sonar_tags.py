import os
import sys
from pathlib import Path
import pdb
import json
from pathlib import Path
from collections import Counter

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

tag_dict = {src: {} for src in lang_id_map.keys()}

def get_tags(filepath):
    tags = []
    with open(filepath, "r") as f:
        contents = json.load(f)
        for part in contents:
            # if "tags" in part:
            #     tags += part["tags"]
            # if "type" in part:
            #     tags.append(part["type"])
            # if "impacts" in part and "severity" in part["impacts"]:
            if part["impacts"][0]["severity"] in ["CRITICAL", "BLOCKER"]:
                # if "message" in part:
                tags.append(part["message"])
    return tags

def prepare_tags(org_name, project_path):
    for model in MODELS:
        for dataset in LANG_MAP.keys():
            for src in LANG_MAP[dataset].keys():
                for tgt in LANG_MAP[dataset][src]:
                    for mode in MODE_MAP.keys():
                        key = f"{model}_{dataset}_{src}_{tgt}_{mode}"
                        print(key)
                        filepath = os.path.join(project_path, "sonar_report", f"{org_name}_{model}_{dataset}_{lang_id_map[src]}_{lang_id_map[tgt]}_{mode}_Repair_details.json")
                        if not os.path.exists(filepath):
                            o = 0
                        else:
                            tags = get_tags(filepath)
                            if tgt not in tag_dict[src]:
                                tag_dict[src][tgt] = []
                            tag_dict[src][tgt] += tags

def get_counts(tags):
    count = Counter(tags)
    # Get the 4 most common tags
    top_4 = count.most_common(4)
    
    # Create a new Counter
    new_count = Counter(dict(top_4))
    
    # Sum the rest as "others"
    others_count = len(count.values()) - len(new_count.values())
    
    if others_count > 0:
        new_count["others"] = others_count
    
    print(new_count)

if __name__ == "__main__":
    project_path = Path.cwd().parent
    prepare_tags("codenl", project_path)
    # print(tag_dict)
    for src in tag_dict.keys():
        for tgt in tag_dict[src].keys():
            tags = tag_dict[src][tgt]
            print(f"src: {src}, tgt: {tgt}")
            print("-"*50)
            get_counts(tags)
            
            # print(count)
            print("="*50)
            print()


