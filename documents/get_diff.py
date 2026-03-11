import sys
import json
from pathlib import Path


def get_languages(dataset_root, dataset_name):
    dataset_path = dataset_root / dataset_name
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    return sorted([p.name for p in dataset_path.iterdir() if p.is_dir()])


def get_code_files(code_dir):
    if not code_dir.exists():
        return set()
    return {p.name for p in code_dir.iterdir() if p.is_file()}


def compare_language(src_root, filtered_root, dataset_name, lang):
    src_code = src_root / dataset_name / lang / "Code"
    filtered_code = filtered_root / dataset_name / lang / "Code"

    src_files = get_code_files(src_code)
    filtered_files = get_code_files(filtered_code)

    removed = sorted(src_files - filtered_files)
    added = sorted(filtered_files - src_files)
    common = sorted(src_files & filtered_files)

    return {
        "source_count": len(src_files),
        "filtered_count": len(filtered_files),
        "common_count": len(common),
        "removed_count": len(removed),
        "added_count": len(added),
        "removed": removed,
        "added": added,
    }


def compare_dataset(dataset_name, src_root, filtered_root):
    langs = get_languages(src_root, dataset_name)

    result = {
        "dataset": dataset_name,
        "source_root": str(src_root),
        "filtered_root": str(filtered_root),
        "languages": {},
    }

    for lang in langs:
        result["languages"][lang] = compare_language(
            src_root, filtered_root, dataset_name, lang
        )

    return result


def print_report(result):
    print(f"\nDataset: {result['dataset']}")
    print(f"Source root   : {result['source_root']}")
    print(f"Filtered root : {result['filtered_root']}")

    for lang, info in result["languages"].items():
        print(f"\n=== {lang} ===")
        print(f"Source files   : {info['source_count']}")
        print(f"Filtered files : {info['filtered_count']}")
        print(f"Removed files  : {info['removed_count']}")
        print(f"Added files    : {info['added_count']}")

        if info["removed"]:
            print("\nRemoved files:")
            for f in info["removed"]:
                print(f"  {f}")


def main():
    if len(sys.argv) != 4:
        print("Usage:")
        print("python diff_dataset.py <dataset_name> <src_dataset_root> <filtered_dataset_root>")
        print("\nExample:")
        print("python diff_dataset.py avatar dataset_lit dataset_nlspec")
        sys.exit(1)

    dataset_name = sys.argv[1]
    src_root = Path(sys.argv[2])
    filtered_root = Path(sys.argv[3])

    result = compare_dataset(dataset_name, src_root, filtered_root)

    print_report(result)

    output_file = f"diff_{dataset_name}.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nFull diff saved to {output_file}")


if __name__ == "__main__":
    main()
