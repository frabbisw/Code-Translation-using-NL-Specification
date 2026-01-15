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
    f_ext = {"Python":"py", "Java": "java", "C++": "cpp", "C": "c", "Go": "go", "Javascript": "js", "Rust": "rs"}
    
    ################################################################################
    # Argument Parser
    ################################################################################

    parser = argparse.ArgumentParser(description='run translation with GPT-4 with a given dataset and languages')
    parser.add_argument('--dataset', help='dataset to use for code translation. should be one of [codenet,avatar]', required=True, type=str)
    parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--target_lang', help='target language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--model', help='model to use for code translation.', type=str, default="gpt-4o-mini")
    parser.add_argument('--models_dir', help='directory where the models are kept.', type=str, default="")
    parser.add_argument('-n', '--NL_Spec_Phase', help='determine if NL-Spec translation and repair phase will run', action="store_true")
    parser.add_argument('-s', '--Source_Phase', help='determine if Spurce translation and repair phase will run', action="store_true")
    parser.add_argument('-b', '--NL_Spec_Source_Phase', help='determine if NL-Spec + Source translation and repair phase will run', action="store_true")
    args = parser.parse_args()

    dataset = args.dataset
    source = args.source_lang
    target = args.target_lang
    model = args.model
    models_dir = args.models_dir
    nl_spec_phase = args.NL_Spec_Phase
    source_phase = args.Source_Phase
    both_phase = args.NL_Spec_Source_Phase

    ################################################################################
    # Sanity Check of Inputs
    ################################################################################
    if dataset not in ["avatar", "codenet", "codenetintertrans", "evalplus"]:
        print(f"invalid dataset {dataset}")
        exit()
    source_dir = f"{os.getcwd()}/dataset/{dataset}/{source}/Code"
    if os.path.isdir(source_dir) == False:
        print(f"invalid source_dir {source_dir}")
        exit()
    if target not in ["C", "C++", "Go", "Java", "Python", "Rust", "Javascript"]:
        print(f"invalid target lang {target}")
        exit()
    if model not in ["starcoder", "magicoder", "llama"]:
        if "gpt" not in model and "deepseek" not in model:
            print(f"invalid model")
            exit()
    if source == target:
        print(f"source == target {target == source}")
        exit()
    print("Sanity Check of Inputs")

    ################################################################################
    # Instantiate Local Model if under use
    ################################################################################
    model_map = {"magicoder": "Magicoder-S-DS-6.7B", "starcoder": "starcoder2-15b", "llama": "CodeLlama-7b-Instruct-hf"}
    model_name = model
    if model in ["starcoder", "magicoder", "llama"]:
        model = LocalCausalLMRunner(f"{models_dir}/{model_map[model]}")
    print("Instantiate Local Model if under use")


    if source_phase:
        ################################################################################
        # Generate Translation using source (baseline)
        ################################################################################
        ext = f".{f_ext[source]}"
        source_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.endswith(ext)]
        for file in source_files:
            translation_generation_sc.translation_generation_sc(dataset=dataset, source=source, target=target, filename=file, model=model, model_name=model_name)
        print("Generate Translation using source (baseline)")

        ################################################################################
        # Evaluate Previous Phase, Translation using source (baseline)
        ################################################################################
        translated_code_dir = f"{os.getcwd()}/Generations/{model_name}/translation_source/{dataset}/{source}/{target}"
        report_dir = f"{os.getcwd()}/Generations/{model_name}/translation_source/Reports/{dataset}/{source}/{target}"
        phase = "Evaluate Previous Phase, Translation using source (baseline)"
        translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
        print("Evaluate Previous Phase, Translation using source (baseline)")

        ################################################################################
        # Repair Iteration 1 (source)
        ################################################################################
        skip_iter = False
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Generations/{model_name}/translation_source/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Generations/{model_name}/translation_source/Reports/{dataset}/{source}/{target}"
            out_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr1/{dataset}/{source}/{target}"
            tried_fixing = all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)
            if tried_fixing == False:
                skip_iter = True
            print("Repair Iteration 1 (source)")

        ################################################################################
        # Evaluate Previous Phase, Repair Iteration 1 (source)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr1/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr1/Reports/{dataset}/{source}/{target}"
            phase = "Evaluate Previous Phase, Repair Iteration 1 (source)"
            translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
            print("Evaluate Previous Phase, Repair Iteration 1 (source)")

        ################################################################################
        # Repair Iteration 2 (source)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr1/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr1/Reports/{dataset}/{source}/{target}"
            out_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr2/{dataset}/{source}/{target}"
            tried_fixing = all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)
            if tried_fixing == False:
                skip_iter = True
            print("Repair Iteration 2 (source)")

        ################################################################################
        # Evaluate Previous Phase, Repair Iteration 2 (source)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr2/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr2/Reports/{dataset}/{source}/{target}"
            phase = "Evaluate Previous Phase, Repair Iteration 2 (source)"
            translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
            print("Evaluate Previous Phase, Repair Iteration 2 (source)")

        ################################################################################
        # Repair Iteration 3 (source)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr2/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr2/Reports/{dataset}/{source}/{target}"
            out_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr3/{dataset}/{source}/{target}"
            tried_fixing = all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)
            if tried_fixing == False:
                skip_iter = True
            print("Repair Iteration 3 (source)")

        ################################################################################
        # Evaluate Previous Phase, Repair Iteration 3 (source)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr3/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_source/itr3/Reports/{dataset}/{source}/{target}"
            phase = "Evaluate Previous Phase, Repair Iteration 3 (source)"
            translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
            print("Evaluate Previous Phase, Repair Iteration 3 (source)")

    if both_phase or nl_spec_phase:
        ################################################################################
        # Generate Pseudocode
        ################################################################################
        source_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.endswith(ext)]
        for file in source_files:
            pseudocode_generation.pseudocode_generation(dataset=dataset, source=source, filename=file, model=model, model_name=model_name)
        print("Generate Pseudocode")

    if nl_spec_phase:
        ################################################################################
        # Generate Translation Using NL
        ################################################################################
        source_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.endswith(ext)]
        for file in source_files:
            translation_generation_nl.translation_generation_nl(dataset=dataset, source=source, target=target, filename=file, model=model, model_name=model_name)    
        print("Generate Translation Using NL")

        ################################################################################
        # Evaluate Previous Phase, Translation Using NL
        ################################################################################
        translated_code_dir = f"{os.getcwd()}/Generations/{model_name}/translation_nl/{dataset}/{source}/{target}"
        report_dir = f"{os.getcwd()}/Generations/{model_name}/translation_nl/Reports/{dataset}/{source}/{target}"
        phase = "Evaluate Previous Phase, Translation Using NL"
        translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
        print("Evaluate Previous Phase, Translation Using NL")    
    
        ################################################################################
        # Repair Iteration 1 (NL)
        ################################################################################
        skip_iter = False
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Generations/{model_name}/translation_nl/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Generations/{model_name}/translation_nl/Reports/{dataset}/{source}/{target}"
            out_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr1/{dataset}/{source}/{target}"
            tried_fixing = all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)
            if tried_fixing == False:
                skip_iter = True
            print("Repair Iteration 1 (NL)")

        ################################################################################
        # Evaluate Previous Phase, Repair Iteration 1 (NL)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr1/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr1/Reports/{dataset}/{source}/{target}"
            phase = "Evaluate Previous Phase, Repair Iteration 1 (NL)"
            translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
            print("Evaluate Previous Phase, Repair Iteration 1 (NL)")

        ################################################################################
        # Repair Iteration 2 (NL)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr1/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr1/Reports/{dataset}/{source}/{target}"
            out_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr2/{dataset}/{source}/{target}"
            tried_fixing = all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)
            if tried_fixing == False:
                skip_iter = True
            print("Repair Iteration 2 (NL)")


        ################################################################################
        # Evaluate Previous Phase, Repair Iteration 2 (NL)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr2/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr2/Reports/{dataset}/{source}/{target}"
            phase = "Evaluate Previous Phase, Repair Iteration 2 (NL)"
            translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
            print("Evaluate Previous Phase, Repair Iteration 2 (NL)")

        ################################################################################
        # Repair Iteration 3 (NL)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr2/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr2/Reports/{dataset}/{source}/{target}"
            out_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr3/{dataset}/{source}/{target}"
            tried_fixing = all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)
            if tried_fixing == False:
                skip_iter = True
            print("Repair Iteration 3 (NL)")

        ################################################################################
        # Evaluate Previous Phase, Repair Iteration 3 (NL)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr3/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl/itr3/Reports/{dataset}/{source}/{target}"
            phase = "Evaluate Previous Phase, Repair Iteration 3 (NL)"
            translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
            print("Evaluate Previous Phase, Repair Iteration 3 (NL)")


    if both_phase:
        ################################################################################
        # Generate Translation Using NL+SC
        ################################################################################
        source_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.endswith(ext)]
        for file in source_files:
            translation_generation_nl_sc.translation_generation_nl_sc(dataset=dataset, source=source, target=target, filename=file, model=model, model_name=model_name)    
        print("Generate Translation Using NL+SC")

        ################################################################################
        # Evaluate Previous Phase, Translation Using NL+SC
        ################################################################################
        translated_code_dir = f"{os.getcwd()}/Generations/{model_name}/translation_nl_and_source/{dataset}/{source}/{target}"
        report_dir = f"{os.getcwd()}/Generations/{model_name}/translation_nl_and_source/Reports/{dataset}/{source}/{target}"
        phase = "Evaluate Previous Phase, Translation Using NL+SC"
        translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
        print("Evaluate Previous Phase, Translation Using NL+SC")

        ################################################################################
        # Repair Iteration 1 (NL+SC)
        ################################################################################
        skip_iter = False
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Generations/{model_name}/translation_nl_and_source/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Generations/{model_name}/translation_nl_and_source/Reports/{dataset}/{source}/{target}"
            out_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr1/{dataset}/{source}/{target}"
            tried_fixing = all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)
            if tried_fixing == False:
                skip_iter = True
            print("Repair Iteration 1 (NL+SC)")


        ################################################################################
        # Evaluate Previous Phase, Repair Iteration 1 (NL+SC)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr1/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr1/Reports/{dataset}/{source}/{target}"
            phase = "Evaluate Previous Phase, Repair Iteration 1 (NL+SC)"
            translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
            print("Evaluate Previous Phase, Repair Iteration 1 (NL+SC)")

        ################################################################################
        # Repair Iteration 2 (NL+SC)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr1/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr1/Reports/{dataset}/{source}/{target}"
            out_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr2/{dataset}/{source}/{target}"
            tried_fixing = all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)
            if tried_fixing == False:
                skip_iter = True
            print("Repair Iteration 2 (NL+SC)")

        ################################################################################
        # Evaluate Previous Phase, Repair Iteration 2 (NL+SC)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr2/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr2/Reports/{dataset}/{source}/{target}"
            phase = "Evaluate Previous Phase, Repair Iteration 2 (NL+SC)"
            translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
            print("Evaluate Previous Phase, Repair Iteration 2 (NL+SC)")

        ################################################################################
        # Repair Iteration 3 (NL+SC)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr2/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr2/Reports/{dataset}/{source}/{target}"
            out_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr3/{dataset}/{source}/{target}"
            tried_fixing = all_errors_fixation.all_errors_fixation(dataset=dataset,source=source, target=target, translation_dir=translated_code_dir, rep_dir=report_dir, out_dir=out_dir, model=model)
            if tried_fixing == False:
                skip_iter = True
            print("Repair Iteration 3 (NL+SC)")


        ################################################################################
        # Evaluate Previous Phase, Repair Iteration 3 (NL+SC)
        ################################################################################
        if skip_iter == False:
            translated_code_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr3/{dataset}/{source}/{target}"
            report_dir = f"{os.getcwd()}/Repair/{model_name}/translation_nl_and_source/itr3/Reports/{dataset}/{source}/{target}"
            phase = "Evaluate Previous Phase, Repair Iteration 3 (NL+SC)"
            translation_evaluation.translation_evaluation(dataset=dataset, source=source, target=target, translated_code_dir=translated_code_dir, report_dir=report_dir, phase=phase, model=model_name)
            print("Evaluate Previous Phase, Repair Iteration 3 (NL+SC)")

        if isinstance(model, LocalCausalLMRunner):
            print("-"*100)
            print(f"Total Run: {model.total_run}")
            print("-"*100)
