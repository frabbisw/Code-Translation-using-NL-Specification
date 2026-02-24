# run_all_stats.py
import os
import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

from significance_metrics import run_metrics

VALID_EXTS = {".c", ".cpp", ".go", ".java", ".py"}

DATASETS = ["avatar", "codenet", "evalplus"]

LANG_MAP = {
    "codenet": {
        "Python": ["C", "C++", "Java", "Go"],
        "Java": ["C", "C++", "Python", "Go"],
        "C": ["C++", "Java", "Python", "Go"],
        "C++": ["C", "Java", "Python", "Go"],
        "Go": ["C", "C++", "Java", "Python"],
    },
    "avatar": {
        "Python": ["C", "C++", "Java", "Go"],
        "Java": ["C", "C++", "Python", "Go"],
    },
    "evalplus": {
        "Python": ["Java"],
    },
}

# Adjust if you have multiple models
MODELS = ["deepseek"]

# Assumes your repo layout exactly like your current scripts:
# dataset/{dataset}/{source}/Code/*
# Repair/{model}/translation_source/itr3/Reports/{dataset}/{source}/{target}/*.json
# Repair/{model}/translation_nl/itr3/Reports/{dataset}/{source}/{target}/*.json
# Repair/{model}/translation_nl_and_source/itr3/Reports/{dataset}/{source}/{target}/*.json


def discover_universe(universe_dir: str) -> List[str]:
    root = Path(universe_dir)
    if not root.exists():
        raise FileNotFoundError(universe_dir)
    problem_ids: Set[str] = set()
    for f in root.rglob("*"):
        if f.is_file() and f.suffix in VALID_EXTS:
            problem_ids.add(f.stem)
    return sorted(problem_ids)


def extract_file_id(key: str) -> str:
    # key might be "123.py" or "123.some.ext" or similar
    return str(key).split(".", 1)[0]


def unify_error_jsons(input_dir: str, output_json: str) -> None:
    """
    Reads all *.json report files in input_dir, collects failing ids from JSON keys,
    writes unified failures as {"id1":0, "id2":0, ...} into output_json.
    """
    in_dir = Path(input_dir)
    if not in_dir.exists():
        raise FileNotFoundError(f"Missing reports dir: {input_dir}")

    failed_ids: Set[str] = set()
    json_files = sorted(in_dir.glob("*.json"))
    if not json_files:
        # keep it explicit; upstream can decide to skip
        raise FileNotFoundError(f"No JSON report files found in: {input_dir}")

    for jf in json_files:
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"{jf} is not a JSON object")
        for k in data.keys():
            failed_ids.add(extract_file_id(k))

    unified = {fid: 0 for fid in sorted(failed_ids)}
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(unified, f, indent=2)


def safe_metrics_for_pair(
    model: str, dataset: str, source: str, target: str, base_dir: str, out_base: str, seed: int = 0
) -> Optional[Dict[str, Any]]:
    """
    Returns metrics dict, or None if required inputs are missing.
    """
    universe_dir = f"{base_dir}/dataset/{dataset}/{source}/Code"
    if not Path(universe_dir).exists():
        return None

    universe = discover_universe(universe_dir)
    if not universe:
        return None

    out_dir = Path(out_base) / model / dataset / source / target
    out_dir.mkdir(parents=True, exist_ok=True)

    universe_txt = out_dir / "universe.txt"
    with open(universe_txt, "w", encoding="utf-8") as f:
        for pid in universe:
            f.write(pid + "\n")

    # report dirs
    nl_rep_dir = f"{base_dir}/Repair/{model}/translation_nl/itr3/Reports/{dataset}/{source}/{target}"
    sc_rep_dir = f"{base_dir}/Repair/{model}/translation_source/itr3/Reports/{dataset}/{source}/{target}"
    nlsc_rep_dir = f"{base_dir}/Repair/{model}/translation_nl_and_source/itr3/Reports/{dataset}/{source}/{target}"

    # unify failure jsons
    nl_json = str(out_dir / "nl.json")
    sc_json = str(out_dir / "sc.json")
    nlsc_json = str(out_dir / "nlsc.json")

    try:
        unify_error_jsons(nl_rep_dir, nl_json)
        unify_error_jsons(sc_rep_dir, sc_json)
        unify_error_jsons(nlsc_rep_dir, nlsc_json)
    except (FileNotFoundError, ValueError) as e:
        # if any is missing, skip (or you can record the error)
        return {"error": str(e)}

    # compute metrics
    try:
        metrics = run_metrics(str(universe_txt), sc_json, nl_json, nlsc_json, seed=seed)
        return metrics
    except Exception as e:
        return {"error": f"metrics_failed: {e}"}


def main():
    base_dir = os.getcwd()
    out_base = f"{base_dir}/sig_test_data_all"  # new output root
    out_json_path = Path(out_base) / "summary_all.json"
    Path(out_base).mkdir(parents=True, exist_ok=True)

    final: Dict[str, Any] = {}

    for model in MODELS:
        final.setdefault(model, {})
        for dataset in DATASETS:
            final[model].setdefault(dataset, {})
            if dataset not in LANG_MAP:
                continue

            for source, targets in LANG_MAP[dataset].items():
                final[model][dataset].setdefault(source, {})
                for target in targets:
                    metrics = safe_metrics_for_pair(
                        model=model,
                        dataset=dataset,
                        source=source,
                        target=target,
                        base_dir=base_dir,
                        out_base=out_base,
                        seed=0,
                    )
                    if metrics is None:
                        # universe missing; skip silently
                        continue
                    final[model][dataset][source][target] = metrics

    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2)

    print(f"Wrote: {out_json_path}")


if __name__ == "__main__":
    main()
