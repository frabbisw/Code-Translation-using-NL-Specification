import sys
import json
import re
from pathlib import Path
from tqdm import tqdm


def get_languages(dataset_root, dataset_name):
    dataset_path = dataset_root / dataset_name
    return sorted([p.name for p in dataset_path.iterdir() if p.is_dir()])


def parse_avatar(name):
    m = re.match(r"^(.*)_(\d+)\.(in|out)$", name)
    if not m:
        return None
    problem, idx, io = m.groups()
    return f"{problem}|{idx}|{io}"


def parse_codenet(name):
    m1 = re.match(r"^(.*)_(in|out)\.txt$", name)
    if m1:
        prob, io = m1.groups()
        return f"{prob}|{io}"

    m2 = re.match(r"^(.*)\.(in|out)$", name)
    if m2:
        prob, io = m2.groups()
        return f"{prob}|{io}"

    return None


def parse_evalplus(name):
    if name.endswith(".txt"):
        return name.replace(".txt", "")
    return None


def get_parser(dataset):
    if dataset == "avatar":
        return parse_avatar
    if dataset == "codenet":
        return parse_codenet
    if dataset == "evalplus":
        return parse_evalplus
    raise ValueError("Unsupported dataset")


def collect_testcases(testcase_dir, dataset):
    parser = get_parser(dataset)

    keys = set()

    if not testcase_dir.exists():
        return keys

    files = [p for p in testcase_dir.iterdir() if p.is_file()]

    for p in tqdm(files, desc=f"Scanning {testcase_dir}", leave=False):
        k = parser(p.name)
        if k:
            keys.add(k)

    return keys


def compare_language(dataset, src_root, filtered_root, lang):
    src_tc = src_root / dataset / lang / "TestCases"
    filtered_tc = filtered_root / dataset / lang / "TestCases"

    src = collect_testcases(src_tc, dataset)
    filtered = collect_testcases(filtered_tc, dataset)

    removed = sorted(src - filtered)
    added = sorted(filtered - src)

    return {
        "source_count": len(src),
        "filtered_count": len(filtered),
        "removed_count": len(removed),
        "added_count": len(added),
        "removed": removed,
        "added": added
    }


def compare_dataset(dataset, src_root, filtered_root):
    langs = get_languages(src_root, dataset)

    result = {"dataset": dataset, "languages": {}}

    for lang in langs:
        result["languages"][lang] = compare_language(
            dataset, src_root, filtered_root, lang
        )

    return result


def print_report(res):
    print(f"\nDataset: {res['dataset']}")

    for lang, info in res["languages"].items():
        print(f"\n=== {lang} ===")
        print("Source testcases :", info["source_count"])
        print("Filtered         :", info["filtered_count"])
        print("Removed          :", info["removed_count"])
        print("Added            :", info["added_count"])


def main():
    if len(sys.argv) != 4:
        print("Usage:")
        print("python diff_testcases_simple.py <dataset> <src_root> <filtered_root>")
        sys.exit(1)

    dataset = sys.argv[1]
    src_root = Path(sys.argv[2])
    filtered_root = Path(sys.argv[3])

    res = compare_dataset(dataset, src_root, filtered_root)

    print_report(res)

    with open(f"testcase_diff_{dataset}.json", "w") as f:
        json.dump(res, f, indent=2)

    print("\nSaved JSON report.")


if __name__ == "__main__":
    main()
