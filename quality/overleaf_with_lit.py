import glob
import json
import os
from os.path import join

lang_map = {
    "py": "Py",
    "cpp": "C++",
    "java": "Java",
    "c": "C",
    "go": "Go",
}

def generate_latex_table(data, output_file="table.tex"):
    # Define the LaTeX table header with custom column widths
    # header = r"\begin{tabular}{|p{3cm}|p{2cm}|p{2cm}|l|l|l|l|}"
    # header += r"\hline"
    # header += r"Dataset & Src & Tgt & BF & AF & BF & AF \\ \hline"
    header = ""
    # Prepare the rows of the table
    rows = ""
    for i, row in enumerate(data):
        # Assuming each row in 'data' is a tuple or list of values in the format
        # (Dataset, Src, Tgt, BF, AF, BF, AF)
        if i == 7:
            rows += " & ".join(str(item) for item in row) + " \\\\ \\midrule \n"
        elif i == 27:
            rows += " & ".join(str(item) for item in row) + " \\\\ \\midrule \n"
        elif i == 28:
            rows += " & ".join(str(item) for item in row) + " \\\\ \\bottomrule \n"
        else:
            rows += " & ".join(str(item) for item in row) + " \\\\ \n"

    # Define the LaTeX table footer
    # footer = r"\end{tabular}"
    footer = ""
    # Combine the header, rows, and footer into the final table content
    table_content = header + rows + footer

    # Write the LaTeX table to a file
    with open(output_file, "w") as f:
        f.write(table_content)
    print(f"Table has been written to {output_file}")

data = []

bf_nl_summary_folder = "outputs/ours/nl_only"
bf_src_summary_folder = "outputs/ours/src_nl"
af_nl_summary_folder = "outputs/ours/repair_nl_only"
af_src_summary_folder = "outputs/ours/repair_src_nl"
bf_lit_summary_folder = "outputs/lit/fix-0"
af_lit_summary_folder = "outputs/lit/fix-1"

bf_nl_file_names = [f for f in os.listdir(bf_nl_summary_folder) if f.startswith('summary') and f.endswith('.json')]

numbers_map = {"avatar": {"py": 239, "java": 240},
               "codenet": {"py": 200, "java": 200, "cpp": 200, "c": 200, "go": 200},
               "evalplus": {"py": 164, "java": 164, "cpp": 164, "c": 164, "go": 164}}

for bf_nl_file_name in bf_nl_file_names:
    _, dataset, src, tgt, __ = bf_nl_file_name.split("/")[-1].split("_")
    with open(join(bf_lit_summary_folder, bf_nl_file_name), "r") as f:
        bf_lit_content = json.load(f)
        bf_lit_BC = bf_lit_content["severity"].get("CRITICAL", 0) + bf_lit_content["severity"].get("BLOCKER", 0)
        bf_lit_T = bf_lit_content.get("total", 0)
    with open(join(af_lit_summary_folder, bf_nl_file_name), "r") as f:
        af_lit_content = json.load(f)
        af_lit_BC = af_lit_content["severity"].get("CRITICAL", 0) + af_lit_content["severity"].get("BLOCKER", 0)
        af_lit_T = af_lit_content.get("total", 0)
    with open(join(bf_nl_summary_folder, bf_nl_file_name), "r") as f:
        bf_nl_content = json.load(f)
        bf_nl_BC = bf_nl_content["severity"].get("CRITICAL", 0) + bf_nl_content["severity"].get("BLOCKER", 0)
        bf_nl_T = bf_nl_content.get("total", 0)
    with open(join(bf_src_summary_folder, bf_nl_file_name), "r") as f:
        bf_src_content = json.load(f)
        bf_src_BC = bf_src_content["severity"].get("CRITICAL", 0) + bf_src_content["severity"].get("BLOCKER", 0)
        bf_src_T = bf_src_content.get("total", 0)
    with open(join(af_nl_summary_folder, bf_nl_file_name), "r") as f:
        af_nl_content = json.load(f)
        af_nl_BC = af_nl_content["severity"].get("CRITICAL", 0) + af_nl_content["severity"].get("BLOCKER", 0)
        af_nl_T = af_nl_content.get("total", 0)
    with open(join(af_src_summary_folder, bf_nl_file_name), "r") as f:
        af_src_content = json.load(f)
        af_src_BC = af_src_content["severity"].get("CRITICAL", 0) + af_src_content["severity"].get("BLOCKER", 0)
        af_src_T = af_src_content.get("total", 0)
    # data.append([dataset, lang_map[src], lang_map[tgt], f"{bf_nl_BC}/{bf_nl_T}", "N/A", f"{bf_src_BC}/{bf_src_T}", "N/A"])
    tmp_data = [bf_lit_BC, round((bf_lit_BC / numbers_map[dataset][src]), 2), af_lit_BC, round((af_lit_BC / numbers_map[dataset][src]), 2), bf_nl_BC, round((bf_nl_BC / numbers_map[dataset][src]), 2), af_nl_BC, round((af_nl_BC / numbers_map[dataset][src]), 2), bf_src_BC, round((bf_src_BC / numbers_map[dataset][src]), 2), af_src_BC, round((af_src_BC / numbers_map[dataset][src]), 2)]
    min_value = min(tmp_data)
    data.append([dataset, lang_map[src], lang_map[tgt]] +
                [r"\textbf{"+f"{tmp_data[2*i]} ({tmp_data[2*i+1]})"+"}"
                 if tmp_data[2*i+1] <= min_value
                 else f"{tmp_data[2*i]} ({tmp_data[2*i+1]})"
                 for i in range(int(len(tmp_data)/2))])
    # data.append([dataset, lang_map[src], lang_map[tgt],
    #              f"{bf_lit_BC} ({round((bf_lit_BC / numbers_map[dataset][src]), 2)})", f"{af_lit_BC} ({round((af_lit_BC / numbers_map[dataset][src]), 2)})",
    #              f"{bf_nl_BC} ({round((bf_nl_BC / numbers_map[dataset][src]), 2)})", f"{af_nl_BC} ({round((af_nl_BC / numbers_map[dataset][src]), 2)})",
    #              f"{bf_src_BC} ({round((bf_src_BC / numbers_map[dataset][src]), 2)})", f"{af_src_BC} ({round((af_src_BC / numbers_map[dataset][src]), 2)})"])

data.sort(key=lambda x: (x[0], x[1], x[2]))
generate_latex_table(data)
