import os
import openai
from openai import OpenAI
import logging
import tiktoken
from pathlib import Path
from dotenv import load_dotenv
import re
import argparse
from tqdm import tqdm
import Constants
import compiler

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
        "C#": "cs"
    }

    def __init__(self, dataset, model) -> None:
        self.model = model
        self.dataset = dataset

    def __enter__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key
        logging.info(f"successfully set up openai api key")

        self.main_dir = os.getcwd()
        self.output_dir = os.path.join(self.main_dir, "repair_nl_and_source/debug_on_translated_codes_itr4")

        # Find the input directory with all the code examples
        self.input_dir = Path(self.main_dir).joinpath("dataset", self.dataset)

        self.hf_cache_dir = os.path.join(self.main_dir, "hf_cache_dir")

        if not self.input_dir.exists():
            logging.error(f"directory {str(self.input_dir)} does not exist. raising FileNotFoundError")
            raise FileNotFoundError(f"Directory {str(self.input_dir)} does not exist.")

        self.out_dir = Path(self.output_dir).joinpath(self.dataset)
        if not self.out_dir.exists():
            self.out_dir.mkdir(parents=True)

        return self

    def send_message_to_openai(self, message_log):
        "Use OpenAI's ChatCompletion API to get the chatbot's response"
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        num_tokens = len(encoding.encode(message_log[1]["content"]))

        response = "exceptional case"
        is_success = False
        max_attempts = 5
        client = OpenAI()
        while max_attempts > 0:
            try:
                response = client.chat.completions.create(
                    model=self.model,  # The name of the OpenAI chatbot model to use
                    # The conversation history up to this point, as a list of dictionaries
                    messages=message_log,
                    # The maximum number of tokens (words or subwords) in the generated response
                    max_tokens=max(1, 8000-num_tokens),
                    # The "creativity" of the generated response (higher temperature = more creative)
                    temperature=0.7,
                )
                is_success = True
                break
            except openai.error.InvalidRequestError as e:
                return "# Token size exceeded."
            except:
                max_attempts -= 1
                continue

        if not is_success:
            return response

        # Find the first response from the chatbot that has text in it (some responses may not have text)
        for choice in response.choices:
            if "text" in choice:
                return choice.text

        # If no response with text is found, return the first response's content (which may be empty)
        return response.choices[0].message.content

    def debug_with_OPENAI(self, source, code_as_str, to, error_details):
        content = code_as_str + f"\n# The above code of {to} has one or more compilation errors. Error details: {error_details} Fix the compilation error.\nPrint only the {to} code and end with the comment \End of Code\. Do not add any extra explanations or any other text except the {to} code."

        message = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": content}]
        response = self.send_message_to_openai(message)
        return response.replace("cpp\n", "").replace(f"```{to.lower()}", "").replace("```", "")
    
    def debug_compile_error_general(self, source, target, translation_dir):
        input_dir = Path(self.main_dir).joinpath(translation_dir, f"{self.dataset}/{source}/{target}")
        #remove all .class files
        dir_files = os.listdir(str(input_dir))
        for file in dir_files:
            if ".class" in file: os.remove(str(input_dir) +"/"+ file)

        # snippets = list(input_dir.iterdir())
        snippets = [f for f in list(input_dir.iterdir()) if str(f).split(".")[-1] in ["py", "java", "c", "cpp", "go", "c++"]]

        compile_error_snippets = []
        compile_error_info = {}
        print(f"Finding Compilation Errors for {source} to {target} from {self.dataset} dataset:")
        for source_file in tqdm(snippets, total=len(snippets), bar_format="{desc:<5.5}{percentage:3.0f}%|{bar:10}{r_bar}"):
            if source_file.stem == "__pycache__":
                continue
            verdict, error_info = compiler.compile(str(input_dir), source_file.name, target)

            if verdict == Constants.COMPILATION_ERROR:
                compile_error_snippets.append(source_file)
                compile_error_info[source_file] = error_info

        #remove all .class files generated
        dir_files = os.listdir(str(input_dir))
        for file in dir_files:
            if ".class" in file: os.remove(str(input_dir) +"/"+ file)

        dir_files = os.listdir(os.getcwd())
        for file in dir_files:
            if "exec_output" in file: os.remove(os.getcwd() +"/"+ file)
            if ".o" in file: os.remove(os.getcwd() +"/"+ file)

        print(f"Generating Repaired Code: found errors {len(compile_error_snippets)}")
        for source_file in tqdm(compile_error_snippets, total=len(compile_error_snippets), bar_format="{desc:<5.5}{percentage:3.0f}%|{bar:10}{r_bar}"):
            code_id = source_file.stem
            if code_id == "__pycache__":
                continue
            code_as_str = source_file.read_text(encoding="utf-8")

            target_dir = self.out_dir.joinpath(f"{source}", f"{target}")
            if not target_dir.exists():
                target_dir.mkdir(parents=True)

            filename_of_translated_code = target_dir.joinpath(f"{code_id}.{Debug.EXTENSTIONS[target]}")

            filename_of_translated_prompt = target_dir.joinpath(f"{code_id}.txt")

            translated_code_fp = Path(filename_of_translated_code)

            with open(filename_of_translated_prompt, "w") as f:
                content = code_as_str + f"\n# The above code of {target} has one or more compilation errors. Error details: {compile_error_info[source_file]} Fix the compilation error.\nPrint only the {target} code and end with the comment \End of Code\. Do not add any extra explanations or any other text except the {target} code."
                print(content, file=f)
                f.close()
            if translated_code_fp.exists():
                continue

            translated_code = self.debug_with_OPENAI(source, code_as_str, target, compile_error_info[source_file])
            translated_code = re.sub('public\s*class\s*.+', 'public class ' + code_id + ' {', translated_code)

            with open(filename_of_translated_code, "w") as f:
                if len(translated_code) > 1:
                    print(translated_code, file=f)
                else:
                    print(code_as_str, file=f)
                    
    def __exit__(self, exception, _, __):
        print(exception)


if __name__ == "__main__":

    load_dotenv()

    parser = argparse.ArgumentParser(description='run debug with a given dataset and languages')
    parser.add_argument('--dataset', help='dataset to use for code debug. should be one of [codenet,avatar,evalplus]', required=True, type=str)
    parser.add_argument('--source_lang', help='source language to use for code debug. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--target_lang', help='target language to use for code debug. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--translation_dir', help='path to directory to get the translated files to test', required=True, type=str)
    args = parser.parse_args()

    source = args.source_lang
    target = args.target_lang
    dataset = args.dataset
    model = "gpt-4o-mini"
    translation_dir = args.translation_dir
    with Debug(dataset, model) as debugger:
        logging.info(f"debugging (compilation errors) from {source} to {target} using {model} and {dataset} dataset")          
        debugger.debug_compile_error_general(source, target, translation_dir)
