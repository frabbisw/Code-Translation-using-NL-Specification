import os
import numpy as np
from os.path import join
import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# py c cpp java go

# root = "outputs"
types = ["fix-0", "fix-1", "nl_only", "src_nl", "repair_nl_only", "repair_src_nl"]
titles = ["Translation with LIT", "Repair with LIT", "Translation with NL-Only", "Translation with Source-NL", "Repair with NL-Only", "Repair with Source-NL"]
languages = ["py", "c", "cpp", "java", "go"]


def get_two_d(root, trans_type, target_datasets):
    files = [f for f in os.listdir(join(root, trans_type)) if f.startswith("summary") and f.endswith(".json")]
    two_d = {}
    for file in files:
        with open(join(root, trans_type, file), 'r') as f:
            nl_only_data = json.load(f)
            _, dataset, src, trg, __ = file.split("_")
            if dataset not in target_datasets:
                continue
            if src not in two_d:
                two_d[src] = {}
            noi = nl_only_data["severity"].get("BLOCKER", 0) + nl_only_data["severity"].get("CRITICAL", 0)
            ncloc = int(nl_only_data["ncloc"])
            if trg not in two_d[src]:
                two_d[src][trg] = [0, 0]
            tmp_1, tmp_2 = two_d[src][trg]
            two_d[src][trg] = [tmp_1+noi, tmp_2+ncloc]
                # round((1000 * noi / ncloc), 2)
    for src in two_d.keys():
        for trg in two_d[src].keys():
            two_d[src][trg] = round((1000 * two_d[src][trg][0] / two_d[src][trg][1]), 2)
    return two_d

def gen_heat_map(data, name, title):
    df = pd.DataFrame(data)
    df = df.reindex(languages, axis=0).reindex(languages, axis=1)
    df = df.fillna(0)
    plt.figure(figsize=(12, 10))
    ax = sns.heatmap(df, annot=True, cmap="YlGnBu", cbar=True, linewidths=0.5,
                annot_kws={"size": 28},  # Increase size of the annotation text in cells
                fmt="g", vmin=0, vmax=50)
                # cbar_kws={'label': 'Scale'})
    plt.title(title, fontsize=32)
    plt.xlabel("Source Languages", fontsize=30)
    plt.ylabel("Target Languages", fontsize=30)

    plt.xticks(fontsize=28)  # X-axis tick labels font size
    plt.yticks(fontsize=28)  # Y-axis tick labels font size

    colorbar = ax.collections[0].colorbar
    colorbar.ax.tick_params(labelsize=28)
    colorbar.set_ticks([0, 10, 20, 30, 40, 50])  # Set specific tick values for the colorbar

    # plt.show()
    plt.savefig(f"figures/heatmap_{name}.png", bbox_inches='tight')


# violin_info = {"nl_only": "BF - PC",
#                "nl_with_source": "BF - SP",
#                "repair_nl_only": "AF - PC",
#                "repair_nl_with_source": "AF - SP",}

def gen_box_plot(cats_info, name, xlabel):
    data = {
        'Repaired LIT': [v2 for k1, v1 in cats_info[0].items() for k2, v2 in v1.items()],
        'Repaired NL': [v2 for k1, v1 in cats_info[1].items() for k2, v2 in v1.items()],
        'Repaired NL-SRC': [v2 for k1, v1 in cats_info[2].items() for k2, v2 in v1.items()]
    }

    df = pd.DataFrame(data)

    # Melt the data for easy plotting (long format)
    df_melted = df.melt(var_name='Type', value_name='Value')

    # Create the violin plot
    plt.figure(figsize=(12, 10))
    sns.violinplot(x='Type', y='Value', data=df_melted, inner="quart", hue="Type", palette="coolwarm", density_norm="width")
    sns.scatterplot(x='Type', y='Value', data=df_melted, color='black', marker='o', s=100, zorder=3)

    # Add titles and labels
    # plt.title("Violin Plot of Issues per 1000 lines of codes for Different Types (NL and Repair)", fontsize=16)
    plt.xlabel(xlabel, fontsize=30)
    plt.ylabel("Issues Count", fontsize=30)

    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)  # Y-axis tick labels font size
    plt.ylim(-20, 70)

    # Show the plot
    # plt.show()
    plt.savefig(f"figures/violin_{name}.png", bbox_inches='tight')

dataset_info = {"codenet": "CodNet",
                "avatar": "Avatar",
                "evalplus": "EvalPlus",
                "all": "All"}

for d in [["codenet"], ["avatar"], ["evalplus"], ["all", "codenet", "avatar", "evalplus"]]:
    cats_info = []
    for i, t in enumerate(["fix-1", "repair_nl_only", "repair_src_nl"]):
        two_d = get_two_d("outputs/ours", t, d)
        cats_info.append(two_d)
        # gen_heat_map(two_d, f"{t}_{d[0]}", f"Issues per 1k for {dataset_info[d[0]]}")
    gen_box_plot(cats_info,  f"{d[0]}", f"{dataset_info[d[0]]}")

# print(nl_only_two_d)
