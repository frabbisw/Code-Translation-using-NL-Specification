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
    header = r"\begin{tabular}{|p{3cm}|p{2cm}|p{2cm}|l|l|l|l|}"
    header += r"\hline"
    header += r"Dataset & Src & Tgt & BF & AF & BF & AF \\ \hline"

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
    footer = r"\end{tabular}"

    # Combine the header, rows, and footer into the final table content
    table_content = header + rows + footer

    # Write the LaTeX table to a file
    with open(output_file, "w") as f:
        f.write(table_content)
    print(f"Table has been written to {output_file}")


data = []

bf_nl_summary_folder = "outputs/nl_only"
bf_src_summary_folder = "outputs/src_nl"
af_nl_summary_folder = "outputs/repair_nl_only"
af_src_summary_folder = "outputs/repair_src_nl"

bf_nl_file_names = [f for f in os.listdir(bf_nl_summary_folder) if f.startswith('summary') and f.endswith('.json')]
# bf_src_file_names = [f for f in os.listdir(bf_src_summary_folder) if f.startswith('summary') and f.endswith('.json')]
# af_nl_file_names = [f for f in os.listdir(af_nl_summary_folder) if f.startswith('summary') and f.endswith('.json')]
# af_src_file_names = [f for f in os.listdir(af_src_summary_folder) if f.startswith('summary') and f.endswith('.json')]

for bf_nl_file_name in bf_nl_file_names:
    _, dataset, src, tgt, __ = bf_nl_file_name.split("/")[-1].split("_")
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
    if dataset == "codenet":
        data.append([dataset, lang_map[src], lang_map[tgt], f"{bf_nl_BC} ({round((bf_nl_BC / 240), 2)})",
                     f"{af_nl_BC} ({round((af_nl_BC / 240), 2)})", f"{bf_src_BC} ({round((bf_src_BC / 240), 2)})",
                     f"{af_src_BC} ({round((af_src_BC / 240), 2)})"])
    elif dataset == "avatar":
        data.append([dataset, lang_map[src], lang_map[tgt], f"{bf_nl_BC} ({round((bf_nl_BC / 200), 2)})",
                     f"{af_nl_BC} ({round((af_nl_BC / 200), 2)})", f"{bf_src_BC} ({round((bf_src_BC / 200), 2)})",
                     f"{af_src_BC} ({round((af_src_BC / 200), 2)})"])
    elif dataset == "evalplus":
        data.append([dataset, lang_map[src], lang_map[tgt], f"{bf_nl_BC} ({round((bf_nl_BC / 164), 2)})",
                     f"{af_nl_BC} ({round((af_nl_BC / 164), 2)})", f"{bf_src_BC} ({round((bf_src_BC / 164), 2)})",
                     f"{af_src_BC} ({round((af_src_BC / 164), 2)})"])

data.sort(key=lambda x: (x[0], x[1], x[2]))
generate_latex_table(data)
