import os
import sys
from pathlib import Path

models = ["gpt4", "magicoder", "deepseek"]
datasets = ["codenet", "avatar", "codenetintertrans"]
trans_type = ["translation_nl", "translation_nl_and_source", "translation_source"]
lang_map = {
    "codenet": {
        "Python": ["C", "C++", "Java", "Go"],
        "Java": ["C", "C++", "Python", "Go"],
        "C": ["C++", "Java", "Python", "Go"],
        "C++": ["C", "Java", "Python", "Go"],
        "Go": ["C", "C++", "Java", "Python"]
    },
    "avatar": {
        "Java": ["Python"],
        "Python": ["Java"]
    },
    "codenetintertrans": {
        "C++": ["Java", "Python", "Rust", "Go", "JavaScript"],
        "Java": ["C++", "Python", "Rust", "Go", "JavaScript"],
        "Python": ["C++", "Java", "Rust", "Go", "JavaScript"],
        "Rust": ["C++", "Java", "Python", "Go", "JavaScript"],
        "Go": ["C++", "Java", "Python", "Rust", "JavaScript"],
        "JavaScript": ["C++", "Java", "Python", "Rust", "Go"]
    },
    "evalplus": {
        "Python": ["Java"]
    }
}
lang_instances = {
  "codenet": 200, 
  "avatar": 240,
  "codenetintertrans": 35,
  "evalplus": 164,
}
def get_score_lang(filepath, total):
  if not os.path.exists(file_path):
    return -1
  incorrects, corrects = 0, 0
  with open(filepath, "r") as f:
    lines = [l.strip() for l in f.readlines()]
    for l in lines:
      if l.startswith("Total Instances:"):
        incorrects = int(l.split(":")[-1].strip())
      elif l.startswith("Total Correct:")
        corrects = int(l.split(":")[-1].strip())
    return total - incorrects + corrects

for d in datasets:
  for model in models:
    for t in trans_type:
      for sl in lang_map.keys():
        number_of_target_langs = len(lang_map[d][sl])
        sum_score = 0
        for tl in lang_map[sl]:
          tl_score = get_score_lang(f"Repair/{model}/{t}/itr3/Reports/{d}/{sl}/{tl}/{d}_compileReport_from_{sl}_to_{tl}.txt", lang_instances[d])
          if tl_score < 0:
            tl_score = get_score_lang(f"Repair/{model}/{t}/itr2/Reports/{d}/{sl}/{tl}/{d}_compileReport_from_{sl}_to_{tl}.txt", lang_instances[d])
            if tl_score < 0:
              tl_score = 0
              number_of_target_langs -= 1
        sum_score += tl_score
        if number_of_target_langs > 0:
          cell_score = round(100 * sum_score / (number_of_target_langs * lang_instances[d]), 2)
        else:
          cell_score = "NA"
        print(d, model, t, sl, cell_score)
        
    
