import json
import numpy as np
from statsmodels.stats.contingency_tables import mcnemar

def load_fail_set(path: str) -> set[str]:
    """
    JSON can be:
      - {"p1": 1, "p2": 1, ...}  (keys are failures)
      - ["p1", "p2", ...]        (list of failures)
    We treat keys/items as the failing problem ids.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return set(map(str, data.keys()))
    if isinstance(data, list):
        return set(map(str, data))
    raise ValueError(f"{path} must be a JSON dict or list representing failures.")

def load_universe(path: str) -> list[str]:
    """
    One problem_id per line.
    """
    with open(path, "r", encoding="utf-8") as f:
        ids = [line.strip() for line in f if line.strip()]
    if not ids:
        raise ValueError(f"Universe file {path} is empty.")
    return ids

def bootstrap_ci(x: np.ndarray, n=10000, alpha=0.05, seed=0):
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n):
        sample = rng.choice(x, size=len(x), replace=True)
        means.append(sample.mean())
    lo = float(np.quantile(means, alpha / 2))
    hi = float(np.quantile(means, 1 - alpha / 2))
    return lo, hi

def mcnemar_exact(a: np.ndarray, b: np.ndarray):
    # regressions (a=1,b=0), fixes (a=0,b=1)
    b_reg = int(((a == 1) & (b == 0)).sum())
    c_fix = int(((a == 0) & (b == 1)).sum())
    table = [[0, b_reg],
             [c_fix, 0]]
    p = float(mcnemar(table, exact=True).pvalue)
    return p, b_reg, c_fix

def summarize(name: str, arr: np.ndarray):
    rate = float(arr.mean())
    lo, hi = bootstrap_ci(arr)
    print(f"{name:10s}: rate={rate:.4f}  95%CI=[{lo:.4f}, {hi:.4f}]  (n={len(arr)})")

    return f"[{lo:.3g}, {hi:.3g}]"

def run(universe_txt: str, source_fail_json: str, nl_fail_json: str, nl_source_fail_json: str):
    ids = load_universe(universe_txt)

    src_fail = load_fail_set(source_fail_json)
    nl_fail  = load_fail_set(nl_fail_json)
    nls_fail = load_fail_set(nl_source_fail_json)

    # Convert failures-only into pass arrays: pass=1 if NOT in fail set
    src_arr = np.array([0 if pid in src_fail else 1 for pid in ids], dtype=int)
    nl_arr  = np.array([0 if pid in nl_fail  else 1 for pid in ids], dtype=int)
    nls_arr = np.array([0 if pid in nls_fail else 1 for pid in ids], dtype=int)

    print(f"\nUniverse size: {len(ids)}")
    print(f"Failures: source={len(src_fail)}  nl={len(nl_fail)}  nl_source={len(nls_fail)}\n")
    success_rate_sc = ((len(ids) - len(src_fail)) / len(ids)) * 100
    print(f"Success Rate (SC):{success_rate_sc}%")

    summarize("source", src_arr)
    nl = summarize("nl", nl_arr)
    nl_sc = summarize("nl_source", nls_arr)

    print("\nMcNemar exact (paired) comparisons:")
    p, b, c = mcnemar_exact(src_arr, nl_arr)
    print(f"  source vs nl       : p={p:.6g}  regressions(b)={b}  fixes(c)={c}")
    output = f"{len(ids)}, {success_rate_sc:.3g}, {p:.3g}, {c}/{b}, "

    p, b, c = mcnemar_exact(src_arr, nls_arr)
    print(f"  source vs nl_source: p={p:.6g}  regressions(b)={b}  fixes(c)={c}")
    output = output + f"{p:.3g}, {c}/{b}"

    p, b, c = mcnemar_exact(nl_arr, nls_arr)
    print(f"  nl vs nl_source    : p={p:.6g}  regressions(b)={b}  fixes(c)={c}")

    return output

# if __name__ == "__main__":
#     import argparse
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--universe", required=True, help="Text file: one problem_id per line (all evaluated ids).")
#     ap.add_argument("--source_fail", required=True, help="JSON containing ONLY failing ids for source.")
#     ap.add_argument("--nl_fail", required=True, help="JSON containing ONLY failing ids for nl.")
#     ap.add_argument("--nl_source_fail", required=True, help="JSON containing ONLY failing ids for nl+source.")
#     args = ap.parse_args()

#     run(args.universe, args.source_fail, args.nl_fail, args.nl_source_fail)