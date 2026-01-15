import argparse
import os
from pathlib import Path
import shutil

def collect_and_copy(src_folder:Path, copy_folder:Path, translation_files:set):
    f_ext = ["py", "java", "c", "cpp", "go", "js", "rs"]
    if not src_folder.exists():
        return translation_files

    for file in src_folder.iterdir():
        if file.is_file() and file.suffix.lstrip(".") in f_ext and file.name not in translation_files:
            translation_files.add(file.name)
            shutil.copy2(file, copy_folder / file.name)

    return translation_files

def copy_translation_files(model, phase, dataset, source, target, copy_folder):
    Path(copy_folder).mkdir(parents=True, exist_ok=True)
    translation_files = set()
    translation_files = collect_and_copy(Path(f"{os.getcwd()}/Repair/{model}/{phase}/itr3/{dataset}/{source}/{target}"), Path(copy_folder), translation_files)
    translation_files = collect_and_copy(Path(f"{os.getcwd()}/Repair/{model}/{phase}/itr2/{dataset}/{source}/{target}"), Path(copy_folder), translation_files)
    translation_files = collect_and_copy(Path(f"{os.getcwd()}/Repair/{model}/{phase}/itr1/{dataset}/{source}/{target}"), Path(copy_folder), translation_files)
    translation_files = collect_and_copy(Path(f"{os.getcwd()}/Generations/{model}/{phase}/{dataset}/{source}/{target}"), Path(copy_folder), translation_files)


if __name__ == "__main__":
    ################################################################################
    # Argument Parser
    ################################################################################

    parser = argparse.ArgumentParser(description='run translation with GPT-4 with a given dataset and languages')
    parser.add_argument('--dataset', help='dataset to use for code translation. should be one of [codenet,avatar]', required=True, type=str)
    parser.add_argument('--source_lang', help='source language', required=True, type=str)
    parser.add_argument('--target_lang', help='target language', required=True, type=str)
    parser.add_argument('--model', help='model to consider', type=str, default="gpt-4o-mini")
    args = parser.parse_args()

    dataset = args.dataset
    source = args.source_lang
    target = args.target_lang
    model = args.model

    root_folder = f"{os.getcwd()}/SonarQube_Ready_Artifacts/"
    os.makedirs(root_folder, exist_ok=True)

    phase = "translation_source"
    copy_folder = f"{root_folder}/{model}/{phase}/{dataset}/{source}/{target}"
    copy_translation_files(model=model, phase=phase, dataset=dataset, source=source, target=target, copy_folder=copy_folder)
    phase = "translation_nl"
    copy_folder = f"{root_folder}/{model}/{phase}/{dataset}/{source}/{target}"
    copy_translation_files(model=model, phase=phase, dataset=dataset, source=source, target=target, copy_folder=copy_folder)
    phase = "translation_nl_and_source"
    copy_folder = f"{root_folder}/{model}/{phase}/{dataset}/{source}/{target}"
    copy_translation_files(model=model, phase=phase, dataset=dataset, source=source, target=target, copy_folder=copy_folder)

