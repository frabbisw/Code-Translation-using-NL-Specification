import json
from collections import defaultdict
from pathlib import Path

INPUT_JSON = "sig_test_data_all/summary_all.json"
MODEL = "deepseek"


def fmt_p(p):
    if p < 1e-4:
        return f"{p:.2e}"
    if p == 1:
        return "1"
    return f"{p:.4g}"


def fmt_cb(c, b):
    return f"{c}/{b}"


def fmt_rate_pct(r):
    return f"{r * 100:.1f}"


def fmt_gain_pct(g):
    # g is in [0,1], show percentage points with sign
    return f"{g * 100:+.1f}"


def load_data():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)[MODEL]


def latex_escape(s):
    return s.replace("_", "\\_")


def generate_rows(data):
    rows = defaultdict(list)

    for dataset, ds_data in data.items():
        for src, src_data in ds_data.items():
            for tgt, stats in src_data.items():
                if not isinstance(stats, dict) or "error" in stats:
                    continue

                total = stats["source"]["n"]
                sc_rate = stats["source"]["rate"]

                # McNemar
                m_sc_nl = stats["mcnemar"]["source_vs_nl"]
                m_sc_nls = stats["mcnemar"]["source_vs_nl_source"]

                # Unions
                u_nl_nls = stats["union"]["nl_or_nl_source"]["rate"]
                u_all3 = stats["union"]["source_or_nl_or_nl_source"]["rate"]

                row = {
                    "dataset": dataset,
                    "pair": f"{src}$\\rightarrow${tgt}",
                    "total": total,
                    "sc_rate": fmt_rate_pct(sc_rate),
                    "p_sc_nl": fmt_p(m_sc_nl["p_value"]),
                    "cb_sc_nl": fmt_cb(m_sc_nl["fixes_c"], m_sc_nl["regressions_b"]),
                    "p_sc_nls": fmt_p(m_sc_nls["p_value"]),
                    "cb_sc_nls": fmt_cb(m_sc_nls["fixes_c"], m_sc_nls["regressions_b"]),
                    # Combining effect vs SC
                    "u_nl_nls_rate": fmt_rate_pct(u_nl_nls),
                    "u_nl_nls_gain": fmt_gain_pct(u_nl_nls - sc_rate),
                    "u_all3_rate": fmt_rate_pct(u_all3),
                    "u_all3_gain": fmt_gain_pct(u_all3 - sc_rate),
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
        "outcomes ($\\alpha$ = 0.05). "
        "Union columns show the combining effect (ensemble by OR) and gains are reported in percentage points over SC."
    )
    lines.append("}")

    lines.append("\\resizebox{\\textwidth}{!}{")
    lines.append(
        "\\begin{tabular}{|m{1.2cm}|m{1.7cm}|m{1.0cm}|m{1.3cm}|"
        "m{1.05cm}|m{1.05cm}|m{1.15cm}|m{1.15cm}|"
        "m{1.35cm}|m{1.0cm}|m{1.55cm}|m{1.0cm}|}"
    )
    lines.append("\\hline")
    lines.append(
        "\\textbf{Dataset} & \\textbf{SL$\\rightarrow$TL} & \\textbf{Total} & "
        "\\textbf{SC (\\%)} & "
        "\\textbf{p (SC vs NL)} & \\textbf{c/b} & "
        "\\textbf{p (SC vs NL+SC)} & \\textbf{c/b} & "
        "\\textbf{Union (NL$\\cup$NL+SC) (\\%)} & \\textbf{$\\Delta$} & "
        "\\textbf{Union (SC$\\cup$NL$\\cup$NL+SC) (\\%)} & \\textbf{$\\Delta$} \\\\"
    )
    lines.append("\\hline")

    for dataset, ds_rows in rows.items():
        ds_rows = sorted(ds_rows, key=lambda x: x["pair"])
        multirow = len(ds_rows)

        for i, r in enumerate(ds_rows):
            base = (
                f"{r['pair']} & {r['total']} & {r['sc_rate']} & "
                f"{r['p_sc_nl']} & {r['cb_sc_nl']} & "
                f"{r['p_sc_nls']} & {r['cb_sc_nls']} & "
                f"{r['u_nl_nls_rate']} & {r['u_nl_nls_gain']} & "
                f"{r['u_all3_rate']} & {r['u_all3_gain']} \\\\"
            )
            if i == 0:
                lines.append(f"\\multirow{{{multirow}}}{{*}}{{{latex_escape(dataset.capitalize())}}} & {base}")
            else:
                lines.append(f" & {base}")

        lines.append("\\hline")

    lines.append("\\end{tabular}")
    lines.append("}")
    lines.append("\\label{tab:significance_result_union}")
    lines.append("\\end{table*}")

    return "\n".join(lines)


def main():
    data = load_data()
    rows = generate_rows(data)
    latex = generate_latex_table(rows)

    out_path = Path("significance_table_with_union.tex")
    out_path.write_text(latex, encoding="utf-8")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
