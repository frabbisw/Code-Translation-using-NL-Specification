import os
import openai
from openai import OpenAI
import logging
import tiktoken
from dotenv import load_dotenv
import argparse
from tqdm import tqdm
from pathlib import Path
import json
import pandas as pd
import compiler
import Constants

os.makedirs(f'logs', exist_ok=True)
logging.basicConfig(filename=f"logs/translation_evaluation_repair_source.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def send_message_to_openai(message_log):
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
                model="gpt-4o-mini",  # The name of the OpenAI chatbot model to use
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

def repair_code(content, to):
    message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": content}]
    response = send_message_to_openai(message)
    return response.replace("cpp\n", "").replace(f"```{to.lower()}", "").replace("```", "")

def remove_unnecessary_files(current_code_dir):
    #remove all .class and output files generated
    dir_files = os.listdir(current_code_dir)
    for file in dir_files:
        if ".class" in file: os.remove(current_code_dir +"/"+ file)

    dir_files = os.listdir(os.getcwd())
    for file in dir_files:
        if "exec_output" in file: os.remove(os.getcwd() +"/"+ file)

def generate_report(source_lang, target_lang, report_dir, dataset, compile_failed, runtime_failed, test_failed, infinite_loop, infinite_loop_dict, test_passed, test_failed_dict, runtime_failed_dict, test_failed_details, runtime_failed_details, compile_failed_dict):
    txt_fp = Path(report_dir).joinpath(f"{dataset}_compileReport_from_"+str(source_lang)+"_to_"+str(target_lang)+".txt")
    with open(txt_fp, "w", encoding="utf-8") as report:

        total_test_passed = len(test_passed)
        total_compile_fail = len(list(compile_failed_dict.keys()))
        total_test_mismatch = len(list(test_failed_dict.keys()))
        total_runtime = len(list(runtime_failed_dict.keys()))
        total_inf = len(list(infinite_loop_dict.keys()))
        total = total_test_passed+total_compile_fail+total_runtime+total_test_mismatch+total_inf

        report.writelines("Total Instances: {}\n\n".format(total))
        report.writelines("Total Correct: {}\n".format(total_test_passed))
        report.writelines("Total Runtime Failed: {}\n".format(total_runtime))
        report.writelines("Total Compilation Failed: {}\n".format(total_compile_fail))
        report.writelines("Total Test Failed: {}\n".format(total_test_mismatch))
        report.writelines("Total Infinite Loop: {}\n\n".format(total_inf))
        report.writelines("Accuracy: {}\n".format((total_test_passed/total) * 100))
        report.writelines("Runtime Rate: {}\n".format((len(runtime_failed)/total) * 100))
        report.writelines("Compilation Rate: {}\n".format((len(compile_failed)/total) * 100))
        report.writelines("Test Failed Rate: {}\n".format((len(test_failed)/total) * 100))
        report.writelines("Infinite Loop Rate: {}\n\n".format((len(infinite_loop)/total) * 100))
        report.writelines("=================================================================================================\n")
        report.writelines("Failed Test Files: {} \n".format(test_failed))
        report.writelines("Failed Test Details: {} \n".format(test_failed_details))
        report.writelines("=================================================================================================\n")
        report.writelines("Runtime Error Files: {} \n".format(runtime_failed))
        report.writelines("Runtime Error Details: {} \n".format(runtime_failed_details))
        report.writelines("=================================================================================================\n")
        report.writelines("Compilation Error Files: {} \n".format(compile_failed))
        report.writelines("=================================================================================================\n")    
        report.writelines("Infinite Loop Files: {} \n".format(infinite_loop))
        report.writelines("=================================================================================================\n")


    json_fp_testfail = Path(report_dir).joinpath(f"{dataset}_test_fail_report_from_"+str(source_lang)+"_to_"+str(target_lang)+".json")
    json_fp_runtime = Path(report_dir).joinpath(f"{dataset}_runtime_error_report_from_"+str(source_lang)+"_to_"+str(target_lang)+".json")
    json_fp_compile = Path(report_dir).joinpath(f"{dataset}_comiple_error_report_from_"+str(source_lang)+"_to_"+str(target_lang)+".json")
    json_fp_inf = Path(report_dir).joinpath(f"{dataset}_inf_loop_report_from_"+str(source_lang)+"_to_"+str(target_lang)+".json")

    with open(json_fp_testfail, "w", encoding="utf-8") as json_fp_testfail_report:
        json.dump(test_failed_dict, json_fp_testfail_report, indent=4)
    with open(json_fp_runtime, "w", encoding="utf-8") as json_fp_runtime_report:
        json.dump(runtime_failed_dict, json_fp_runtime_report, indent=4)
    with open(json_fp_compile, "w", encoding="utf-8") as json_fp_compile_report:
        json.dump(compile_failed_dict, json_fp_compile_report, indent=4)
    with open(json_fp_inf, "w", encoding="utf-8") as json_fp_inf:
        json.dump(infinite_loop_dict, json_fp_inf, indent=4)

    df = pd.DataFrame(columns=['Source Language', 'Target Language', 'Filename', 'BugType', 'RootCause', 'Impact', 'Comments'])
    index = 0
    for i in range(0, len(compile_failed)):
        list_row = [source_lang, target_lang, compile_failed[i], "", "", "Compilation Error", ""]
        df.loc[i] = list_row
        index+=1
    for i in range(0, len(runtime_failed)):
        list_row = [source_lang, target_lang, runtime_failed[i], "", "", "Runtime Error", ""]
        df.loc[index] = list_row
        index+=1 
    for i in range(0, len(test_failed)):
        list_row = [source_lang, target_lang, test_failed[i], "", "", "Test Failed", ""]
        df.loc[index] = list_row
        index+=1
    
    excel_fp = Path(report_dir).joinpath(f"{dataset}_compileReport_from_"+str(source_lang)+"_to_"+str(target_lang)+".xlsx")
    df.to_excel(excel_fp, sheet_name='Sheet1')

    ordered_unsuccessful_fp = Path(report_dir).joinpath(f"{dataset}_compileReport_from_"+str(source_lang)+"_to_"+str(target_lang)+"_ordered_unsuccessful.txt")
    with open(ordered_unsuccessful_fp, 'w') as f:
        for unsuccessful_instance in compile_failed + runtime_failed + test_failed + infinite_loop:
            f.write(f"{unsuccessful_instance}\n")

def test_avatar(source_lang, target_lang, report_dir, translation_dir, test_dir):
    # txt_fp = Path(report_dir).joinpath(f"{model}_avatar_compileReport_from_"+str(source_lang)+"_to_"+str(target_lang)+".txt")
    # if txt_fp.exists():
    #     print(f"Skipping translation from {source_lang} to {target_lang} as report is already present.")
    #     return

    files = [f for f in os.listdir(translation_dir) if f.split(".")[-1] in ["py", "java", "c", "cpp", "go", "c++"]]
    compile_failed = []
    compile_failed_dict = {}
    test_passed =[]
    test_failed =[]
    test_failed_details = []
    test_failed_dict = {}
    runtime_failed = []
    runtime_failed_details= []
    runtime_failed_dict = {}
    infinite_loop = []
    infinite_loop_dict = {}

    desc = f"Running Avatar Tests for {source_lang} to {target_lang}"

    for i in tqdm(range(len(files)), desc = desc):
        if (not os.path.isfile(f"{translation_dir}/{files[i]}")):
            continue
        tests_passed = 0
        for j in range(1000):
            if os.path.exists(test_dir+"/"+ files[i].split(".")[0]+f"_{j}.in") == False:
                if tests_passed == j:
                    test_passed.append(files[i])
                break
                
            with open(test_dir+"/"+ files[i].split(".")[0]+f"_{j}.in" , 'r') as f:
                f_in = f.read()
            f_out = open(test_dir+"/"+ files[i].split(".")[0]+f"_{j}.out", "r").read()

            verdict, report, _ = compiler.test(translation_dir, files[i], f_in, f_out, target_lang)
            
            if verdict == Constants.TEST_PASSED:
                tests_passed += 1
            elif verdict == Constants.TEST_MISMATCH:
                test_failed.append(files[i])
                test_failed_details.append('Test Index: '+str(j)+' Filename: '+files[i]+ ' ' + report)

                if f"{files[i]}" not in runtime_failed_dict:
                    if f"{files[i]}" in test_failed_dict:
                        temp = test_failed_dict[f"{files[i]}"]
                        test_failed_dict[f"{files[i]}"] = f"{temp}\nTest Index: {j}\n{report}\n"
                    else:
                        test_failed_dict[f"{files[i]}"] = f"Test Index: {j}\n{report}\n"

            elif verdict == Constants.RUNTIME_ERROR:
                runtime_failed.append(files[i])
                runtime_failed_details.append('Test Index: '+str(j)+' Filename: '+ files[i]+' ' + report)

                if f"{files[i]}" not in test_failed_dict:
                    if f"{files[i]}" in runtime_failed_dict:
                        temp = runtime_failed_dict[f"{files[i]}"]
                        runtime_failed_dict[f"{files[i]}"] = f"{temp}\nTest Index: {j}\n{report}\n"
                    else:
                        runtime_failed_dict[f"{files[i]}"] = f"Test Index: {j}\n{report}\n"

            elif verdict == Constants.INFINITE_LOOP:
                if f"{files[i]}" not in test_failed_dict and f"{files[i]}" not in test_failed_dict:
                    infinite_loop.append(files[i])
                    infinite_loop_dict[f"{files[i]}"] = f"{report}\n"
                    break
            elif verdict == Constants.COMPILATION_ERROR:
                compile_failed.append(files[i])
                compile_failed_dict[f"{files[i]}"] = f"{report}\n"
                break

    test_failed = list(set(test_failed))
    test_failed_details = list(set(test_failed_details))
    runtime_failed = list(set(runtime_failed))
    runtime_failed_details = list(set(runtime_failed_details))
    compile_failed = list(set(compile_failed))
    infinite_loop = list(set(infinite_loop))
    test_passed = list(set(test_passed))

    for instance in infinite_loop[:]:
        if instance in test_failed:
            infinite_loop.remove(instance)

    generate_report(source_lang, target_lang, report_dir, "avatar", compile_failed, runtime_failed, test_failed, infinite_loop, infinite_loop_dict, test_passed, test_failed_dict, runtime_failed_dict, test_failed_details, runtime_failed_details, compile_failed_dict)
    remove_unnecessary_files(translation_dir)

def test_codenet(source_lang, target_lang, report_dir, translation_dir, test_dir):
    files = [f for f in os.listdir(translation_dir) if f.split(".")[-1] in ["py", "java", "c", "cpp", "go", "c++"]]
    compile_failed = []
    compile_failed_dict = {}
    test_passed =[]
    test_failed =[]
    test_failed_details = []
    test_failed_dict = {}
    runtime_failed = []
    runtime_failed_details= []
    runtime_failed_dict = {}
    infinite_loop = []
    infinite_loop_dict = {}

    desc = f"Running Codenet Tests for {source_lang} to {target_lang}"
    for i in tqdm(range(len(files)), desc = desc):
        if (not os.path.isfile(f"{translation_dir}/{files[i]}")):
            continue
        
        with open(test_dir+"/"+ files[i].split(".")[0]+".in" , 'r') as f:
            f_in = f.read()
        f_out = open(test_dir+"/"+ files[i].split(".")[0]+".out", "r").read()

        verdict, report, _ = compiler.test(translation_dir, files[i], f_in, f_out, target_lang)

        if verdict == Constants.TEST_PASSED:
            test_passed.append(files[i])
        elif verdict == Constants.TEST_MISMATCH:
            test_failed.append(files[i])
            test_failed_details.append('Filename: '+files[i]+ ' ' + report)
            test_failed_dict[f"{files[i]}"] = f"{report}\n"

        elif verdict == Constants.RUNTIME_ERROR:
            runtime_failed.append(files[i])
            runtime_failed_details.append('Filename: '+ files[i]+ ' ' + report)
            runtime_failed_dict[f"{files[i]}"] = f"{report}\n"

        elif verdict == Constants.INFINITE_LOOP:
            infinite_loop.append(files[i])
            infinite_loop_dict[f"{files[i]}"] = f"{report}\n"
            
        elif verdict == Constants.COMPILATION_ERROR:
            compile_failed.append(files[i])
            compile_failed_dict[f"{files[i]}"] = f"{report}\n"

    test_failed = list(set(test_failed))
    test_failed_details = list(set(test_failed_details))
    runtime_failed = list(set(runtime_failed))
    runtime_failed_details = list(set(runtime_failed_details))
    compile_failed = list(set(compile_failed))
    infinite_loop = list(set(infinite_loop))
    test_passed = list(set(test_passed))

    generate_report(source_lang, target_lang, report_dir, "codenet", compile_failed, runtime_failed, test_failed, infinite_loop, infinite_loop_dict, test_passed, test_failed_dict, runtime_failed_dict, test_failed_details, runtime_failed_details, compile_failed_dict)
    remove_unnecessary_files(translation_dir)

def evaluation_code(dataset, translation_dir, test_dir, report_dir, source, target):
    if dataset == "avatar":
        test_avatar(source, target, report_dir, translation_dir, test_dir)
    elif dataset == "codenet":
        test_codenet(source, target, report_dir, translation_dir, test_dir)

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description='run translation with GPT-4 with a given dataset and languages')
    parser.add_argument('--dataset', help='dataset to use for code translation. should be one of [codenet,avatar]', required=True, type=str)
    parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--target_lang', help='target language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    # parser.add_argument('--filename', help='path to source code', required=True, type=str)
    args = parser.parse_args()

    source = args.source_lang
    target = args.target_lang
    dataset = args.dataset

    if source == target:
        exit()
    # filename = args.filename
    
    # file_basename = filename.split(".")[0]
    # file_ext = "c"
    # if target == "Java":
    #     file_ext = "java"
    # elif target == "Python":
    #     file_ext = "py"
    # elif target == "Go":
    #     file_ext = "go"
    # elif target == "C++":
    #     file_ext = "cpp"

    translated_code_dir = f"repair_nl_and_source/combine_debug_results/{dataset}/{source}/{target}"
    test_dir = f"dataset/{dataset}/{source}/TestCases"
    report_dir = f"repair_nl_and_source/combine_debug_results/Reports/{dataset}/{source}/{target}"

    os.makedirs(report_dir, exist_ok=True)

    evaluation_code(dataset, translated_code_dir, test_dir, report_dir, source, target)

    # test_files = [f for f in os.listdir(test_dir) if os.path.isfile(os.path.join(test_dir, f))]
    # corresponding_tests = [f for f in test_files if file_basename in f and ".in" in f]

    # for i in range(len(corresponding_tests)):
    #     pass





    

