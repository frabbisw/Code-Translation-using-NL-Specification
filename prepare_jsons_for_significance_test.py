import os
from pathlib import Path
import json
import utility
import significance_test

VALID_EXTS = {".c", ".cpp", ".go", ".java", ".py"}

def discover_universe(dir: str) -> list[str]:
    root = Path(dir)
    if not root.exists():
        raise FileNotFoundError(dir)

    problem_ids = set()

    for file in root.rglob("*"):
        if file.is_file() and file.suffix in VALID_EXTS:
            problem_ids.add(file.stem)  # filename without extension

    return sorted(problem_ids)

dataset = "avatar"
source = "Java"
target = "C"
model = "deepseek"

out_dir = f"{os.getcwd()}/sig_test_data/{model}/{dataset}/{source}/{target}"

os.makedirs(out_dir, exist_ok=True)

universe_dir = f"{os.getcwd()}/dataset/{dataset}/{source}/Code"

universe = discover_universe(universe_dir)
universe_txt = f"{out_dir}/universe.txt"

with open(universe_txt, "w", encoding="utf-8") as f:
    for pid in universe:
        f.write(pid + "\n")

utility.wait_for_file(universe_txt)

def extract_file_id(key: str) -> str:
    return key.split(".", 1)[0]

def unify_error_jsons(input_dir: str, output_json: str):
    input_dir = Path(input_dir)

    failed_ids = set()

    # Iterate over all JSON files in the directory
    for json_file in input_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError(f"{json_file} is not a JSON object")

        for key in data.keys():
            failed_ids.add(extract_file_id(key))

    # Build unified failure dict
    unified = {fid: 0 for fid in sorted(failed_ids)}

    # Write output
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(unified, f, indent=2)

nl_rep_dir = f"{os.getcwd()}/Repair/{model}/translation_nl/itr3/Reports/{dataset}/{source}/{target}"
nl_json = f"{out_dir}/nl.json"

unify_error_jsons(nl_rep_dir, nl_json)
utility.wait_for_file(nl_json)

sc_rep_dir = f"{os.getcwd()}/Repair/{model}/translation_source/itr3/Reports/{dataset}/{source}/{target}"
sc_json = f"{out_dir}/sc.json"

unify_error_jsons(sc_rep_dir, sc_json)
utility.wait_for_file(sc_json)

nlsc_rep_dir = f"{os.getcwd()}/Repair/{model}/translation_nl_and_source/itr3/Reports/{dataset}/{source}/{target}"
nlsc_json = f"{out_dir}/nlsc.json"

unify_error_jsons(nlsc_rep_dir, nlsc_json)
utility.wait_for_file(nlsc_json)

output = significance_test.run(universe_txt, sc_json, nl_json, nlsc_json)
output = f"{dataset}, {source} -> {target}, {output}"

with open(f"significance_result.txt", "a") as f:
    print(output, file=f)
    f.close()