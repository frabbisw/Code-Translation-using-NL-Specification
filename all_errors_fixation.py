import os
import logging
from pathlib import Path
import re
from local_model import LocalCausalLMRunner
import json
import OpenAICall
import time

os.makedirs(f'logs', exist_ok=True)
logging.basicConfig(filename=f"logs/debugger.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class Debug:
    EXTENSTIONS = {
        "Java": "java",
        "Python": "py",
        "Go": "go",
        "C": "c",
        "C++": "cpp",
        "Rust": "rs",
        "C#": "cs",
        "Javascript": "js",
        "Rust": "rs"
    }

    def __init__(self, dataset, model, out_dir) -> None:
        self.model = model
        self.dataset = dataset

        self.main_dir = os.getcwd()
        # example out_dir = "repair_nl_and_source/debug_on_translated_codes_itr4"
        self.output_dir = out_dir

        # Find the input directory with all the code examples
        self.input_dir = Path(self.main_dir).joinpath("dataset", self.dataset)

        self.hf_cache_dir = os.path.join(self.main_dir, "hf_cache_dir")

        if not self.input_dir.exists():
            logging.error(f"directory {str(self.input_dir)} does not exist. raising FileNotFoundError")
            raise FileNotFoundError(f"Directory {str(self.input_dir)} does not exist.")

        # return self
    
    def __enter__(self):
        pass

    def wait_for_file(self, filepath, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(filepath):
                return True
            time.sleep(0.2)
        return False

    def debug(self, content, language, model):
        message = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": content}]
        if isinstance(model, str) and "gpt" in model:
            print(f"model {model} is selected. fetching response using api ...")
            response = OpenAICall.send_message_to_openai(message, model)
        elif isinstance(model, str) and "deepseek" in model:
            print(f"model {model} is selected. fetching response using api ...")
            response = OpenAICall.send_message_to_deepseek(message)
        elif isinstance(model, LocalCausalLMRunner):
            print(f"model {model.model_name} is selected. running locally ...")
            response = model.run(message)

        return response.replace("cpp\n", "").replace(f"```{language.lower()}", "").replace("```", "")

    def fix_errors(self, rep_dir, translation_dir, dataset, source, target, error_type, model):
        if error_type == "compilation error(s)":
            err_name = "compile_error"
        elif error_type == "infinite loop error(s)":
            err_name = "inf_loop"
        elif error_type == "test mismatch error(s)":
            err_name = "test_fail"
        elif error_type == "runtime error(s)":
            err_name = "runtime_error"

        detailed_report_file = os.path.join(
            rep_dir,
            f"{dataset}_compileReport_from_{source}_to_{target}.txt"
        )

        self.wait_for_file(detailed_report_file, timeout=20)

        with open(detailed_report_file) as f:
            text = f.read()

        total_instances = int(text.split("Total Instances:")[1].splitlines()[0])
        total_correct = int(text.split("Total Correct:")[1].splitlines()[0])

        total_incorrect = total_instances - total_correct

        if total_incorrect == 0:
            return False
        
        json_f = os.path.join(
            rep_dir,
            f"{dataset}_{err_name}_report_from_{source}_to_{target}.json"
        )

        self.wait_for_file(json_f, timeout=20)

        with open(json_f, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        all_fails = list(json_data.keys())
        if len(json_data) > 0:
            print(f"Generating Repaired Code: found {error_type}: {len(all_fails)}")

            for i in range(len(all_fails)):
                source_file = f"{translation_dir}/{all_fails[i]}"
                code_id = Path(source_file).stem
                with open(source_file, "r") as f:
                    code_as_str = f.read()
                    f.close()
                target_dir = Path(self.output_dir)
                if not target_dir.exists():
                    target_dir.mkdir(parents=True)

                filename_of_translated_code = target_dir.joinpath(f"{code_id}.{Debug.EXTENSTIONS[target]}")
                filename_of_translated_prompt = target_dir.joinpath(f"{code_id}.txt")
                translated_code_fp = Path(filename_of_translated_code)
                with open(filename_of_translated_prompt, "w") as f:
                    content = code_as_str + f"\n# The above code of {target} has one or more {error_type}. Error details: {json_data[all_fails[i]]} Fix the {error_type}.\nPrint only the {target} code and end with the comment \End of Code\. Do not add any extra explanations or any other text except the {target} code."
                    print(content, file=f)
                    f.close()
                if translated_code_fp.exists():
                    continue

                translated_code = self.debug(content, target, model)
                translated_code = re.sub('public\s*class\s*.+', 'public class ' + code_id + ' {', translated_code)

                with open(filename_of_translated_code, "w") as f:
                    if len(translated_code) > 1:
                        print(translated_code, file=f)
                    else:
                        print(code_as_str, file=f)

        return True


    def debug_all_error_general(self, dataset, source, target, translation_dir, rep_dir, model):
        tried_fixing = False
        tried_fixing = self.fix_errors(rep_dir, translation_dir, dataset, source, target, "compilation error(s)", model)
        tried_fixing = self.fix_errors(rep_dir, translation_dir, dataset, source, target, "infinite loop error(s)", model)
        tried_fixing = self.fix_errors(rep_dir, translation_dir, dataset, source, target, "test mismatch error(s)", model)
        tried_fixing = self.fix_errors(rep_dir, translation_dir, dataset, source, target, "runtime error(s)", model)
        return tried_fixing

def all_errors_fixation(dataset, source, target, translation_dir, rep_dir, out_dir, model):
    debugger = Debug(dataset, model, out_dir)
    logging.info(f"fixing errors from {source} to {target} using {model} and {dataset} dataset")
    tried_fixing = debugger.debug_all_error_general(dataset, source, target, translation_dir, rep_dir, model)
    return tried_fixing


# if __name__ == "__main__":

#     load_dotenv()

#     parser = argparse.ArgumentParser(description='run debug with a given dataset and languages')
#     parser.add_argument('--dataset', help='dataset to use for code debug. should be one of [codenet,avatar,evalplus]', required=True, type=str)
#     parser.add_argument('--source_lang', help='source language to use for code debug. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
#     parser.add_argument('--target_lang', help='target language to use for code debug. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
#     parser.add_argument('--translation_dir', help='path to directory to get the translated files', required=True, type=str)
#     parser.add_argument('--report_dir', help='path to directory to get the report on translated files', required=True, type=str)
#     parser.add_argument('--out_dir', help='path to directory to save the fixed files', required=True, type=str)
#     parser.add_argument('--model', help='model to use for code translation.', required=True, type=str)
#     parser.add_argument('--models_dir', help='directory where the models are kept.', required = True, type=str)
#     args = parser.parse_args()

#     source = args.source_lang
#     target = args.target_lang
#     dataset = args.dataset
#     out_dir = args.out_dir
#     model = args.model
#     rep_dir = args.report_dir
#     translation_dir = args.translation_dir
#     debugger = Debug(dataset, model, out_dir)
#     logging.info(f"debugging (compilation errors) from {source} to {target} using {model} and {dataset} dataset") 
    
#     model_map = {"magicoder": "Magicoder-S-DS-6.7B", "starcoder": "starcoder2-15b"}
#     if model in ["starcoder", "magicoder"]:
#         models_dir = args.models_dir
#         model = LocalCausalLMRunner(f"{models_dir}/{model_map[model]}")
    
#     debugger.debug_all_error_general(dataset, source, target, translation_dir, rep_dir, model)
