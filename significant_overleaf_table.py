import json
from collections import defaultdict
from pathlib import Path

INPUT_JSON = "sig_test_data_all/summary_all.json"
MODEL = "deepseek"   # change if needed
ALPHA = 0.05


def fmt_p(p):
    if p < 1e-4:
        return f"{p:.2e}"
    if p == 1:
        return "1"
    return f"{p:.4g}"


def fmt_cb(c, b):
    return f"{c}/{b}"


def fmt_rate(r):
    return f"{r * 100:.1f}"


def load_data():
    with open(INPUT_JSON, "r") as f:
        return json.load(f)[MODEL]


def generate_rows(data):
    """
    Returns:
      rows[dataset] = list of row dicts
    """
    rows = defaultdict(list)

    for dataset, ds_data in data.items():
        for src, src_data in ds_data.items():
            for tgt, stats in src_data.items():
                if "error" in stats:
                    continue

                total = stats["source"]["n"]
                sc_rate = stats["source"]["rate"]

                mcn_sc_nl = stats["mcnemar"]["source_vs_nl"]
                mcn_sc_nls = stats["mcnemar"]["source_vs_nl_source"]

                row = {
                    "dataset": dataset,
                    "pair": f"{src}$\\rightarrow${tgt}",
                    "total": total,
                    "sc_rate": fmt_rate(sc_rate),
                    "p_sc_nl": fmt_p(mcn_sc_nl["p_value"]),
                    "cb_sc_nl": fmt_cb(
                        mcn_sc_nl["fixes_c"], mcn_sc_nl["regressions_b"]
                    ),
                    "p_sc_nls": fmt_p(mcn_sc_nls["p_value"]),
                    "cb_sc_nls": fmt_cb(
                        mcn_sc_nls["fixes_c"], mcn_sc_nls["regressions_b"]
                    ),
                }
                rows[dataset].append(row)

    return rows


def latex_escape(s):
    return s.replace("_", "\\_")


def generate_latex_table(rows):
    lines = []

    lines.append("\\begin{table*}")
    lines.append("\\color{blue}")
    lines.append("\\centering")
    lines.append("\\scriptsize")
    lines.append("\\renewcommand{\\arraystretch}{1.1}")
    lines.append("\\caption{\\color{blue}")
    lines.append(
        "Paired significance and complementarity analysis across datasets and language pairs "
        "on DeepSeekCoder result. SC = source-only translation, NL = translation using "
        "\\specS, SL = source language, TL = target languages. "
        "Fixes ($c$) = problems solved by the second method but not by the first, "
        "regressions ($b$) = problems solved by the first method but not by the second. "
        "$p$-values are computed using McNemar’s exact test on paired per-problem outcomes "
        "($\\alpha$ = 0.05)."
    )
    lines.append("}")
    lines.append("\\resizebox{\\textwidth}{!}{")
    lines.append(
        "\\begin{tabular}{|m{1.4cm}|m{1.8cm}|m{1.2cm}|m{1.6cm}|"
        "m{1.2cm}|m{1.2cm}|m{1.4cm}|m{1.4cm}|}"
    )
    lines.append("\\hline")
    lines.append(
        "\\textbf{Dataset} & \\textbf{SL$\\rightarrow$TL} & \\textbf{Total} & "
        "\\textbf{Only Source Correct (\\%)} & "
        "\\textbf{p (SC vs NL)} & \\textbf{c/b (SC vs NL)} & "
        "\\textbf{p (SC vs NL+SC)} & \\textbf{c/b (SC vs NL+SC)} \\\\"
    )
    lines.append("\\hline")

    for dataset, ds_rows in rows.items():
        ds_rows = sorted(ds_rows, key=lambda x: x["pair"])
        multirow = len(ds_rows)

        for i, r in enumerate(ds_rows):
            if i == 0:
                lines.append(
                    f"\\multirow{{{multirow}}}{{*}}{{{latex_escape(dataset.capitalize())}}}"
                    f" & {r['pair']} & {r['total']} & {r['sc_rate']} & "
                    f"{r['p_sc_nl']} & {r['cb_sc_nl']} & "
                    f"{r['p_sc_nls']} & {r['cb_sc_nls']} \\\\"
                )
            else:
                lines.append(
                    f" & {r['pair']} & {r['total']} & {r['sc_rate']} & "
                    f"{r['p_sc_nl']} & {r['cb_sc_nl']} & "
                    f"{r['p_sc_nls']} & {r['cb_sc_nls']} \\\\"
                )

        lines.append("\\hline")

    lines.append("\\end{tabular}")
    lines.append("}")
    lines.append("\\label{tab:significance_result}")
    lines.append("\\end{table*}")

    return "\n".join(lines)


def main():
    data = load_data()
    rows = generate_rows(data)
    latex = generate_latex_table(rows)

    out_path = Path("significance_table.tex")
    with open(out_path, "w") as f:
        f.write(latex)

    print(f"LaTeX table written to: {out_path}")


if __name__ == "__main__":
    main()
