import json
from collections import defaultdict
from pathlib import Path

INPUT_JSON = "sig_test_data_all/summary_all.json"
MODEL = "deepseek"


# def fmt_p(p: float) -> str:
#     if p < 1e-4:
#         return f"{p:.2e}"
#     if p == 1:
#         return "1"
#     return f"{p:.4g}"

def fmt_p(p: float, alpha: float = 0.05) -> str:
    """
    Format p-value to 2 decimals and highlight significant values
    with light gray background.
    """
    # formatting
    if p < 0.005:
        s = "<0.01"
    else:
        s = f"{p:.2f}"

    # highlight significant cells
    if p < alpha:
        return f"\\cellcolor{{gray!20}}{s}"
    return s

def fmt_cb(c: int, b: int) -> str:
    return f"{c}/{b}"


def latex_escape(s: str) -> str:
    return s.replace("_", "\\_")


def load_data():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)[MODEL]


def generate_rows(data):
    rows = defaultdict(list)

    for dataset, ds_data in data.items():
        for src, src_data in ds_data.items():
            for tgt, stats in src_data.items():
                if not isinstance(stats, dict) or "error" in stats:
                    continue

                total = stats["source"]["n"]

                # original McNemar
                m_sc_nl = stats["mcnemar"]["source_vs_nl"]
                m_sc_nls = stats["mcnemar"]["source_vs_nl_source"]

                # union McNemar tests (must exist in JSON now)
                if "mcnemar_union" not in stats:
                    raise KeyError(
                        "Missing 'mcnemar_union' in JSON. "
                        "Please regenerate summary_all.json with new metrics "
                        "that include sc_vs_nl_or_nl_source and sc_vs_sc_or_nl_or_nl_source."
                    )
                mu = stats["mcnemar_union"]
                m_sc_u_nl_nls = mu["sc_vs_nl_or_nl_source"]
                m_sc_u_all3 = mu["sc_vs_sc_or_nl_or_nl_source"]

                row = {
                    "dataset": dataset,
                    "pair": f"{src}$\\rightarrow${tgt}",
                    "total": total,

                    "p_sc_nl": fmt_p(m_sc_nl["p_value"]),
                    "cb_sc_nl": fmt_cb(m_sc_nl["fixes_c"], m_sc_nl["regressions_b"]),

                    "p_sc_nls": fmt_p(m_sc_nls["p_value"]),
                    "cb_sc_nls": fmt_cb(m_sc_nls["fixes_c"], m_sc_nls["regressions_b"]),

                    "p_sc_u_nl_nls": fmt_p(m_sc_u_nl_nls["p_value"]),
                    "cb_sc_u_nl_nls": fmt_cb(
                        m_sc_u_nl_nls["fixes_c"], m_sc_u_nl_nls["regressions_b"]
                    ),

                    "p_sc_u_all3": fmt_p(m_sc_u_all3["p_value"]),
                    "cb_sc_u_all3": fmt_cb(
                        m_sc_u_all3["fixes_c"], m_sc_u_all3["regressions_b"]
                    ),
                }

                rows[dataset].append(row)

    return rows


def generate_latex_table(rows):
    lines = []

    lines.append("\\begin{table*}")
    lines.append("\\color{blue}")
    lines.append("\\centering")
    lines.append("\\scriptsize")
    lines.append("\\renewcommand{\\arraystretch}{1.1}")
    lines.append("\\caption{\\color{blue}")
    lines.append(
        "Paired significance and complementarity analysis across datasets and language pairs on DeepSeekCoder result. "
        "SC = source-only translation, NL = translation using \\specS, SL = source language, TL = target languages. "
        "Fixes ($c$) = problems solved by the second method but not by the first, regressions ($b$) = problems solved by "
        "the first method but not by the second. $p$-values are computed using McNemar’s exact test on paired per-problem "
        "outcomes ($\\alpha$ = 0.05). Union comparisons quantify the combining effect using McNemar’s exact test between SC "
        "and an OR-ensemble of the other strategies."
    )
    lines.append("}")

    lines.append("\\resizebox{\\textwidth}{!}{")
    lines.append(
        "\\begin{tabular}{|m{1.4cm}|m{1.8cm}|m{1.0cm}|m{1.2cm}|m{1.0cm}|m{1.4cm}|m{1.0cm}|m{1.8cm}|m{1.0cm}|m{2.2cm}|m{1.0cm}|}"
    )
    lines.append("\\hline")

    lines.append(
        "\\textbf{Dataset} & \\textbf{SL$\\rightarrow$TL} & \\textbf{Total} & "
        "\\textbf{p (SC vs NL)} & \\textbf{c/b} & "
        "\\textbf{p (SC vs NL+SC)} & \\textbf{c/b} & "
        "\\textbf{p (SC vs NL$\\cup$(NL+SC))} & \\textbf{c/b} & "
        "\\textbf{p (SC vs SC$\\cup$NL$\\cup$(NL+SC))} & \\textbf{c/b} \\\\"
    )
    lines.append("\\hline")

    for dataset in sorted(rows.keys()):
        ds_rows = sorted(rows[dataset], key=lambda r: r["pair"])
        multirow = len(ds_rows)

        for i, r in enumerate(ds_rows):
            base = (
                f"{r['pair']} & {r['total']} & "
                f"{r['p_sc_nl']} & {r['cb_sc_nl']} & "
                f"{r['p_sc_nls']} & {r['cb_sc_nls']} & "
                f"{r['p_sc_u_nl_nls']} & {r['cb_sc_u_nl_nls']} & "
                f"{r['p_sc_u_all3']} & {r['cb_sc_u_all3']} \\\\"
            )
            if i == 0:
                lines.append(
                    f"\\multirow{{{multirow}}}{{*}}{{{latex_escape(dataset.capitalize())}}} & {base}"
                )
            else:
                lines.append(f" & {base}")

        lines.append("\\hline")

    lines.append("\\end{tabular}")
    lines.append("}")
    lines.append("\\label{tab:significance_result_union_mcnemar}")
    lines.append("\\end{table*}")

    return "\n".join(lines)


def main():
    data = load_data()
    rows = generate_rows(data)
    latex = generate_latex_table(rows)

    out_path = Path("significance_table_union_mcnemar_only.tex")
    out_path.write_text(latex, encoding="utf-8")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
