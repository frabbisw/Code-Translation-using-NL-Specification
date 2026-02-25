# significance_metrics.py
import json
from typing import Dict, List, Set, Tuple, Any

import numpy as np
from statsmodels.stats.contingency_tables import mcnemar


def load_fail_set(path: str) -> Set[str]:
    """
    JSON can be:
      - {"p1": 1, "p2": 1, ...}  (keys are failures)
      - ["p1", "p2", ...]        (list of failures)
    We treat keys/items as failing problem ids.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return set(map(str, data.keys()))
    if isinstance(data, list):
        return set(map(str, data))
    raise ValueError(f"{path} must be a JSON dict or list representing failures.")


def load_universe(path: str) -> List[str]:
    """One problem_id per line."""
    with open(path, "r", encoding="utf-8") as f:
        ids = [line.strip() for line in f if line.strip()]
    if not ids:
        raise ValueError(f"Universe file {path} is empty.")
    return ids


def bootstrap_ci(x: np.ndarray, n: int = 10000, alpha: float = 0.05, seed: int = 0) -> Tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n):
        sample = rng.choice(x, size=len(x), replace=True)
        means.append(sample.mean())
    lo = float(np.quantile(means, alpha / 2))
    hi = float(np.quantile(means, 1 - alpha / 2))
    return lo, hi


def mcnemar_exact(a: np.ndarray, b: np.ndarray) -> Tuple[float, int, int]:
    """
    a,b are binary success arrays (1=success, 0=failure)
    regressions b_reg: a=1,b=0
    fixes       c_fix: a=0,b=1
    """
    b_reg = int(((a == 1) & (b == 0)).sum())
    c_fix = int(((a == 0) & (b == 1)).sum())
    table = [[0, b_reg], [c_fix, 0]]
    p = float(mcnemar(table, exact=True).pvalue)
    return p, b_reg, c_fix


def _rate_ci(arr: np.ndarray, seed: int = 0) -> Dict[str, float]:
    rate = float(arr.mean())
    lo, hi = bootstrap_ci(arr, seed=seed)
    return {"rate": rate, "ci_low": lo, "ci_high": hi, "n": int(len(arr))}


def _union(*arrs: np.ndarray) -> np.ndarray:
    """Union success: success if any method succeeds."""
    if not arrs:
        raise ValueError("Need at least one array for union.")
    u = arrs[0].copy()
    for a in arrs[1:]:
        u = np.maximum(u, a)
    return u


def complementarity(a: np.ndarray, b: np.ndarray) -> Dict[str, Any]:
    """
    Complementarity between two success arrays:
      - a_only: successes solved only by a
      - b_only: successes solved only by b
      - both: successes solved by both
      - none: solved by neither
      - union_rate and gain over best single
    """
    a_only = int(((a == 1) & (b == 0)).sum())
    b_only = int(((a == 0) & (b == 1)).sum())
    both = int(((a == 1) & (b == 1)).sum())
    none = int(((a == 0) & (b == 0)).sum())
    u = _union(a, b)
    union_rate = float(u.mean())
    best_single = max(float(a.mean()), float(b.mean()))
    return {
        "a_only": a_only,
        "b_only": b_only,
        "both": both,
        "none": none,
        "union_rate": union_rate,
        "best_single_rate": best_single,
        "union_gain": union_rate - best_single,
    }


def run_metrics(
    universe_txt: str,
    source_fail_json: str,
    nl_fail_json: str,
    nl_source_fail_json: str,
    seed: int = 0,
) -> Dict[str, Any]:
    """
    Returns a dict with:
      - success rates + bootstrap 95% CI for source/nl/nl_source
      - McNemar exact p-values (paired) for all pairs
      - Union rates + CI
      - Complementarity
      - NEW: McNemar tests for unions:
          SC vs (NL ∪ NL+SC)
          SC vs (SC ∪ NL ∪ NL+SC)
    """
    ids = load_universe(universe_txt)
    src_fail = load_fail_set(source_fail_json)
    nl_fail = load_fail_set(nl_fail_json)
    nls_fail = load_fail_set(nl_source_fail_json)

    src = np.array([0 if pid in src_fail else 1 for pid in ids], dtype=int)
    nl = np.array([0 if pid in nl_fail else 1 for pid in ids], dtype=int)
    nls = np.array([0 if pid in nls_fail else 1 for pid in ids], dtype=int)

    # Rates + CIs
    src_stats = _rate_ci(src, seed=seed)
    nl_stats = _rate_ci(nl, seed=seed)
    nls_stats = _rate_ci(nls, seed=seed)

    # Pairwise McNemar
    p_src_nl, b_src_nl, c_src_nl = mcnemar_exact(src, nl)
    p_src_nls, b_src_nls, c_src_nls = mcnemar_exact(src, nls)
    p_nl_nls, b_nl_nls, c_nl_nls = mcnemar_exact(nl, nls)

    # Unions
    union_all3 = _union(src, nl, nls)          # SC ∪ NL ∪ (NL+SC)
    union_nl_nls = _union(nl, nls)             # NL ∪ (NL+SC)
    union_src_nl = _union(src, nl)             # SC ∪ NL
    union_src_nls = _union(src, nls)           # SC ∪ (NL+SC)

    # ✅ NEW: McNemar on union outcomes (what your table now expects)
    p_sc_u_nl_nls, b_sc_u_nl_nls, c_sc_u_nl_nls = mcnemar_exact(src, union_nl_nls)
    p_sc_u_all3, b_sc_u_all3, c_sc_u_all3 = mcnemar_exact(src, union_all3)

    out: Dict[str, Any] = {
        "universe_n": int(len(ids)),
        "failures": {
            "source": int(len(src_fail)),
            "nl": int(len(nl_fail)),
            "nl_source": int(len(nls_fail)),
        },

        "source": src_stats,
        "nl": nl_stats,
        "nl_source": nls_stats,

        "mcnemar": {
            "source_vs_nl": {"p_value": p_src_nl, "regressions_b": b_src_nl, "fixes_c": c_src_nl},
            "source_vs_nl_source": {"p_value": p_src_nls, "regressions_b": b_src_nls, "fixes_c": c_src_nls},
            "nl_vs_nl_source": {"p_value": p_nl_nls, "regressions_b": b_nl_nls, "fixes_c": c_nl_nls},
        },

        # ✅ NEW KEY (used by your updated overleaf table script)
        "mcnemar_union": {
            "sc_vs_nl_or_nl_source": {
                "p_value": p_sc_u_nl_nls,
                "regressions_b": b_sc_u_nl_nls,
                "fixes_c": c_sc_u_nl_nls,
            },
            "sc_vs_sc_or_nl_or_nl_source": {
                "p_value": p_sc_u_all3,
                "regressions_b": b_sc_u_all3,
                "fixes_c": c_sc_u_all3,
            },
        },

        "union": {
            "source_or_nl": _rate_ci(union_src_nl, seed=seed),
            "source_or_nl_source": _rate_ci(union_src_nls, seed=seed),
            "nl_or_nl_source": _rate_ci(union_nl_nls, seed=seed),
            "source_or_nl_or_nl_source": _rate_ci(union_all3, seed=seed),
        },

        "complementarity": {
            "source_vs_nl": complementarity(src, nl),
            "source_vs_nl_source": complementarity(src, nls),
            "nl_vs_nl_source": complementarity(nl, nls),
            "nl_or_nl_source_vs_source": {
                "union_rate": float(union_nl_nls.mean()),
                "source_rate": float(src.mean()),
                "gain_over_source": float(union_nl_nls.mean() - src.mean()),
                "extra_solved_over_source": int(((union_nl_nls == 1) & (src == 0)).sum()),
            },
            "all3_vs_best_single": {
                "union_rate": float(union_all3.mean()),
                "best_single_rate": max(float(src.mean()), float(nl.mean()), float(nls.mean())),
                "union_gain": float(union_all3.mean() - max(float(src.mean()), float(nl.mean()), float(nls.mean()))),
                "extra_solved_over_best": int((union_all3 == 1).sum() - max(int(src.sum()), int(nl.sum()), int(nls.sum()))),
            },
        },
    }

    return out
