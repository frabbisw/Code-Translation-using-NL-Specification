import json
import os
from collections import Counter
from os.path import join
from tqdm import tqdm as tq

def get_top_10_tags(root, trg_lang):
    tags = []
    impacts = []
    messages = []

    only_files = [join(f"outputs/{root}", f) for f in os.listdir(f"outputs/{root}") if f.startswith("details") and os.path.isfile(os.path.join(f"outputs/{root}", f))]
    for i, file in tq(enumerate(only_files)):
        _, dataset, src, trg, __ = file.split("/")[-1].split("_")
        if trg != trg_lang:
            continue

        with open(file, "r") as f:
            issues = json.load(f)
            for issue in issues:
                if issue["severity"] in ["BLOCKER", "CRITICAL"]:
                    tags += issue["tags"]
                    impacts += [iss["softwareQuality"] for iss in issue["impacts"]]
                    messages.append(issue["message"])

    count = Counter(messages).most_common(10)
    count = [(c[0], round(100*c[1]/len(messages), 2)) for c in count]

    # return Counter(messages).most_common(10), len(messages)
    return count

res = get_top_10_tags("nl_only", "c")


for r in res:
    print("\\item " + r[0].replace("_", "\\_") + ". " + "(\\textbf{"+str(r[1])+"\\%})")