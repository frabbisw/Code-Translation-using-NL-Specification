from local_model import LocalCausalLMRunner
import argparse
import os
import pseudocode_generation
import translation_generation_sc
import translation_generation_nl
import translation_generation_nl_sc
import translation_evaluation
import all_errors_fixation

if __name__ == "__main__":
    f_ext = {"Python":"py", "Java": "java", "C++": "cpp", "C": "c", "Go": "go"}
    
    ################################################################################
    # Argument Parser
    ################################################################################

    parser = argparse.ArgumentParser(description='run translation with GPT-4 with a given dataset and languages')
    parser.add_argument('--dataset', help='dataset to use for code translation. should be one of [codenet,avatar]', required=True, type=str)
    parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--target_lang', help='target language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--model', help='model to use for code translation.', type=str, default="gpt-4o-mini")
    parser.add_argument('--models_dir', help='directory where the models are kept.', type=str, default="")
    args = parser.parse_args()

    dataset = args.dataset
    source = args.source_lang
    target = args.target_lang
    model = args.model
    models_dir = args.models_dir


    ################################################################################
    # Sanity Check of Inputs
    ################################################################################
    if dataset not in ["avatar", "codenet", "codeintertrans"]:
        exit()
    source_dir = f"{os.getcwd()}/dataset/{dataset}/{source}/Code"
    if os.path.isdir(source_dir) == False:
        exit()
    if target not in ["C", "C++", "Go", "Java", "Python"]:
        exit()
    if model not in ["starcoder", "magicoder"]:
        if "gpt" not in model:
            exit()
    if source == target:
        exit()


    ################################################################################
    # Instantiate Local Model if under use
    ################################################################################
    model_map = {"magicoder": "Magicoder-S-DS-6.7B", "starcoder": "starcoder2-15b"}
    if model in ["starcoder", "magicoder"]:
        model = LocalCausalLMRunner(f"{models_dir}/{model_map[model]}")


    ################################################################################
    # Generate Translation using source (baseline)
    ################################################################################
    ext = f".{f_ext[source]}"
    source_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.endswith(ext)]
    for file in source_files:
        translation_generation_sc.translation_generation_sc(dataset=dataset, source=source, target=target, filename=file, model=model)


    ################################################################################
    # Evaluate Previous Phase, Translation using source (baseline)
    ################################################################################
    translated_code_dir = f"Generations/translation_source/{dataset}/{source}/{target}"
    report_dir = f"Generations/translation_source/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Repair Iteration 1 (source)
    ################################################################################
    translated_code_dir = f"Generations/translation_source/{dataset}/{source}/{target}"
    report_dir = f"Generations/translation_source/Reports/{dataset}/{source}/{target}"
    out_dir = f"Repair/translation_source/itr1/{dataset}/{source}/{target}"
    all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)


    ################################################################################
    # Evaluate Previous Phase, Repair Iteration 1 (source)
    ################################################################################
    translated_code_dir = "Repair/translation_source/itr1/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_source/itr1/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Repair Iteration 2 (source)
    ################################################################################
    translated_code_dir = "Repair/translation_source/itr1/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_source/itr1/Reports/{dataset}/{source}/{target}"
    out_dir = f"Repair/translation_source/itr2/{dataset}/{source}/{target}"
    all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)


    ################################################################################
    # Evaluate Previous Phase, Repair Iteration 2 (source)
    ################################################################################
    translated_code_dir = f"Repair/translation_source/itr2/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_source/itr2/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Repair Iteration 3 (source)
    ################################################################################
    translated_code_dir = "Repair/translation_source/itr2/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_source/itr2/Reports/{dataset}/{source}/{target}"
    out_dir = f"Repair/translation_source/itr3/{dataset}/{source}/{target}"
    all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)


    ################################################################################
    # Evaluate Previous Phase, Repair Iteration 3 (source)
    ################################################################################
    translated_code_dir = f"Repair/translation_source/itr3/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_source/itr3/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Generate Pseudocode
    ################################################################################
    source_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.endswith(ext)]
    for file in source_files:
        pseudocode_generation.pseudocode_generation(dataset=dataset, source=source, filename=file, model=model)


    ################################################################################
    # Generate Translation Using NL
    ################################################################################
    source_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.endswith(ext)]
    for file in source_files:
        translation_generation_nl.translation_generation_nl(dataset=dataset, source=source, target=target, filename=file, model=model)    


    ################################################################################
    # Evaluate Previous Phase, Translation Using NL
    ################################################################################
    translated_code_dir = f"Generations/translation_nl/{dataset}/{source}/{target}"
    report_dir = f"Generations/translation_nl/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Repair Iteration 1 (NL)
    ################################################################################
    translated_code_dir = f"Generations/translation_nl/{dataset}/{source}/{target}"
    report_dir = f"Generations/translation_nl/Reports/{dataset}/{source}/{target}"
    out_dir = f"Repair/translation_nl/itr1/{dataset}/{source}/{target}"
    all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)


    ################################################################################
    # Evaluate Previous Phase, Repair Iteration 1 (NL)
    ################################################################################
    translated_code_dir = "Repair/translation_nl/itr1/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_nl/itr1/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Repair Iteration 2 (NL)
    ################################################################################
    translated_code_dir = "Repair/translation_nl/itr1/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_nl/itr1/Reports/{dataset}/{source}/{target}"
    out_dir = f"Repair/translation_nl/itr2/{dataset}/{source}/{target}"
    all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)


    ################################################################################
    # Evaluate Previous Phase, Repair Iteration 2 (NL)
    ################################################################################
    translated_code_dir = f"Repair/translation_nl/itr2/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_nl/itr2/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Repair Iteration 3 (NL)
    ################################################################################
    translated_code_dir = "Repair/translation_nl/itr2/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_nl/itr2/Reports/{dataset}/{source}/{target}"
    out_dir = f"Repair/translation_nl/itr3/{dataset}/{source}/{target}"
    all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)


    ################################################################################
    # Evaluate Previous Phase, Repair Iteration 3 (NL)
    ################################################################################
    translated_code_dir = f"Repair/translation_nl/itr3/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_nl/itr3/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Generate Translation Using NL+SC
    ################################################################################
    source_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.endswith(ext)]
    for file in source_files:
        translation_generation_nl_sc.translation_generation_nl_sc(dataset=dataset, source=source, target=target, filename=file, model=model)    


    ################################################################################
    # Evaluate Previous Phase, Translation Using NL+SC
    ################################################################################
    translated_code_dir = f"Generations/translation_nl_and_source/{dataset}/{source}/{target}"
    report_dir = f"Generations/translation_nl_and_source/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Repair Iteration 1 (NL+SC)
    ################################################################################
    translated_code_dir = f"Generations/translation_nl_and_source/{dataset}/{source}/{target}"
    report_dir = f"Generations/translation_nl_and_source/Reports/{dataset}/{source}/{target}"
    out_dir = f"Repair/translation_nl_and_source/itr1/{dataset}/{source}/{target}"
    all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)


    ################################################################################
    # Evaluate Previous Phase, Repair Iteration 1 (NL+SC)
    ################################################################################
    translated_code_dir = "Repair/translation_nl_and_source/itr1/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_nl_and_source/itr1/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Repair Iteration 2 (NL+SC)
    ################################################################################
    translated_code_dir = "Repair/translation_nl_and_source/itr1/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_nl_and_source/itr1/Reports/{dataset}/{source}/{target}"
    out_dir = f"Repair/translation_nl_and_source/itr2/{dataset}/{source}/{target}"
    all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)


    ################################################################################
    # Evaluate Previous Phase, Repair Iteration 2 (NL+SC)
    ################################################################################
    translated_code_dir = f"Repair/translation_nl_and_source/itr2/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_nl_and_source/itr2/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)


    ################################################################################
    # Repair Iteration 3 (NL+SC)
    ################################################################################
    translated_code_dir = "Repair/translation_nl_and_source/itr2/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_nl_and_source/itr2/Reports/{dataset}/{source}/{target}"
    out_dir = f"Repair/translation_nl_and_source/itr3/{dataset}/{source}/{target}"
    all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)


    ################################################################################
    # Evaluate Previous Phase, Repair Iteration 3 (NL+SC)
    ################################################################################
    translated_code_dir = f"Repair/translation_nl_and_source/itr3/{dataset}/{source}/{target}"
    report_dir = f"Repair/translation_nl_and_source/itr3/Reports/{dataset}/{source}/{target}"
    translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir)