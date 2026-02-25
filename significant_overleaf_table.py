# significant_overleaf_table.py
import json
from collections import defaultdict
from pathlib import Path

INPUT_JSON = "sig_test_data_all/summary_all.json"
MODEL = "deepseek"
ALPHA = 0.05


def fmt_rate(r: float) -> str:
    """Format correctness percentage"""
    return f"{100 * r:.1f}"


def fmt_p_improvement_only(p: float, fixes_c: int, regressions_b: int, alpha: float = ALPHA) -> str:
    """
    Format p-value to 2 decimals and shade (light gray) ONLY if:
      - statistically significant (p < alpha), AND
      - the second method is better (fixes_c > regressions_b)
    """
    if p < 0.005:
        s = "$<0.01$"
    else:
        s = f"{p:.2f}"

    # if (p < alpha) and (fixes_c > regressions_b): # if only to show the significance and better
    if (p < alpha):
        if (fixes_c > regressions_b):        
            return f"\\cellcolor{{green!40}}{{{s}}}"
        else:
            return f"\\cellcolor{{red!40}}{{{s}}}"
    return s


def fmt_cb(fixes_c: int, regressions_b: int) -> str:
    return f"{fixes_c}/{regressions_b}"


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

                sc_rate = stats["source"]["rate"]

                m_sc_nl = stats["mcnemar"]["source_vs_nl"]
                m_sc_nls = stats["mcnemar"]["source_vs_nl_source"]

                if "mcnemar_union" not in stats:
                    raise KeyError(
                        f"Missing 'mcnemar_union' in JSON for {MODEL}/{dataset}/{src}->{tgt}. "
                        "Re-run run_all_stats.py after updating significance_metrics.py."
                    )

                mu = stats["mcnemar_union"]
                m_sc_u_nl_nls = mu["sc_vs_nl_or_nl_source"]
                m_sc_u_all3 = mu["sc_vs_sc_or_nl_or_nl_source"]

                row = {
                    "dataset": dataset,
                    "pair": f"{src}$\\rightarrow${tgt}",
                    "sc_rate": fmt_rate(sc_rate),

                    "p_sc_nl": fmt_p_improvement_only(
                        m_sc_nl["p_value"], m_sc_nl["fixes_c"], m_sc_nl["regressions_b"]
                    ),
                    "cb_sc_nl": fmt_cb(m_sc_nl["fixes_c"], m_sc_nl["regressions_b"]),

                    "p_sc_nls": fmt_p_improvement_only(
                        m_sc_nls["p_value"], m_sc_nls["fixes_c"], m_sc_nls["regressions_b"]
                    ),
                    "cb_sc_nls": fmt_cb(m_sc_nls["fixes_c"], m_sc_nls["regressions_b"]),

                    "p_sc_u_nl_nls": fmt_p_improvement_only(
                        m_sc_u_nl_nls["p_value"],
                        m_sc_u_nl_nls["fixes_c"],
                        m_sc_u_nl_nls["regressions_b"],
                    ),
                    "cb_sc_u_nl_nls": fmt_cb(
                        m_sc_u_nl_nls["fixes_c"], m_sc_u_nl_nls["regressions_b"]
                    ),

                    "p_sc_u_all3": fmt_p_improvement_only(
                        m_sc_u_all3["p_value"],
                        m_sc_u_all3["fixes_c"],
                        m_sc_u_all3["regressions_b"],
                    ),
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
        "SC = source-only translation, NL = translation using \\\\specS, SL = source language, TL = target languages. "
        "Fixes ($c$) = problems solved by the second method but not by the first, "
        "regressions ($b$) = problems solved by the first method but not by the second. "
        "$p$-values are computed using McNemar’s exact test on paired per-problem outcomes ($\\\\alpha$ = 0.05). "
        "Union comparisons quantify the combining effect using McNemar’s exact test between SC and an OR-ensemble of the other strategies. "
        "Cells shaded in green indicate statistically significant improvements over SC ($p<0.05$ and $c>b$), " 
        "while red indicates statistically significant degradations ($p<0.05$ and $c<b$)."
    )
    lines.append("}")

    lines.append("\\resizebox{\\textwidth}{!}{")
    lines.append(
        "\\begin{tabular}{|m{1.4cm}|m{1.8cm}|m{1.2cm}|"
        "m{1.2cm}|m{1.0cm}|"
        "m{1.4cm}|m{1.0cm}|"
        "m{1.8cm}|m{1.0cm}|"
        "m{2.2cm}|m{1.0cm}|}"
    )
    lines.append("\\hline")

    lines.append(
        "\\textbf{Dataset} & \\textbf{SL$\\rightarrow$TL} & \\textbf{SC (\\%)} & "
        "\\textbf{p (SC vs NL)} & \\textbf{c/b} & "
        "\\textbf{p (SC vs NL+SC)} & \\textbf{c/b} & "
        "\\textbf{p (SC vs NL $\\cup$(NL+SC))} & \\textbf{c/b} & "
        "\\textbf{p (SC vs SC$\\cup$ NL$\\cup$(NL+SC))} & \\textbf{c/b} \\\\"
    )
    lines.append("\\hline")

    for dataset in sorted(rows.keys()):
        ds_rows = sorted(rows[dataset], key=lambda r: r["pair"])
        multirow = len(ds_rows)

        for i, r in enumerate(ds_rows):
            base = (
                f"{r['pair']} & {r['sc_rate']} & "
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
    lines.append("\\label{tab:significance_result}")
    lines.append("\\end{table*}")

    return "\n".join(lines)


def main():
    data = load_data()
    rows = generate_rows(data)
    latex = generate_latex_table(rows)

    out_path = Path("significance_table_union_mcnemar_with_sc_rate.tex")
    out_path.write_text(latex, encoding="utf-8")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
