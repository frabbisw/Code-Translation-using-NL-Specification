import Constants
import compiler
import os
from tqdm import tqdm
from pathlib import Path
import json

def repair_tests():
    initial_result = {}
    test_case_dir = "test_cases_original/avatar"
    with open("./avatar_initial_test_cleanup/avatar_ground_truths_errors_Java.json", "r") as initial_cleanup_report_file:
        initial_result = json.load(initial_cleanup_report_file)
        initial_cleanup_report_file.close()
    
    init_res_compile = initial_result["test_mismatch"]

    for key, val in init_res_compile.items():
        code_file = str(key)
        test_file = str(val["Test_file"])
        actual_output = str(val["Actual"])
        generated_output = str(val["Generated"])

        if actual_output.strip().endswith("..."):
            output_first_part = actual_output[:-3]
            if generated_output.startswith(output_first_part):
                code_file_name_parts = code_file.replace(".", "_").split("_")
                if code_file_name_parts[0] == "codeforces":
                    output_test_case_no = test_file.split("_")[0]
                    output_file_name = f"{output_test_case_no}_output"
                    print(test_file)
                    print(output_file_name)
                    x = input()
                    current_test_case_file = f"{test_case_dir}/{code_file_name_parts[0]}/{code_file_name_parts[1]}_{code_file_name_parts[2]}/samples/{output_file_name}"
                    with open(current_test_case_file, "w") as f:
                        f.write(generated_output)
                        f.close()
                elif code_file_name_parts[0] == "atcoder":
                    current_test_case_file = f"{test_case_dir}/{code_file_name_parts[0]}/{code_file_name_parts[1]}_{code_file_name_parts[2]}/out/{test_file}"
                    with open(current_test_case_file, "w") as f:
                        f.write(generated_output)
                
def remove_extension(dir):
    for filename in os.listdir(dir):
        # Split the filename and its extension
        name, _ = os.path.splitext(filename)
    
        # Define the new filename without the extension
        new_filename = name
    
        # Construct full old and new file paths
        old_file_path = os.path.join(dir, filename)
        new_file_path = os.path.join(dir, new_filename)
    
        # Rename the file
        os.rename(old_file_path, new_file_path)

def cleanup_avatar_tests():
    avatar_dataset_dir = "dataset/avatar"
    avatar_test_cases_dir = "test_cases_original/avatar"
    avatar_pls = ["Java", "Python"]

    for j in range(len(avatar_pls)):
        current_code_dir = f"{avatar_dataset_dir}/{avatar_pls[j]}/Code"
        cleaned_test_case_dir = f"{avatar_dataset_dir}/{avatar_pls[j]}/TestCases"

        os.makedirs(cleaned_test_case_dir, exist_ok=True)

        all_files = os.listdir(current_code_dir)

        total_test_for_pl = 0
        failed_test = 0
        compilation_error_report = {}
        total_compilation_failed = 0
        runtime_error_report = {}
        total_runtime_failed = 0
        test_mismatch_report = {}
        total_test_mismatch = 0
        inf_loop_report = {}
        total_inf_loop = 0
        token_limit_report = []
        total_token_limit = 0

        desc = f"Processing Files for {avatar_pls[j]}"

        for i in tqdm(range(len(all_files)), desc=desc):
            current_file = all_files[i]
            current_file_w_o_ext = current_file.split(".")[0]
            filename_parts = current_file.replace(".", "_").split("_")

            if filename_parts[2] == "pycache":
                continue

            current_file_tests_dir = f"{avatar_test_cases_dir}/codeforces/{filename_parts[1]}_{filename_parts[2]}/samples/"
            current_file_inputs_dir = f"{current_file_tests_dir}"
            current_file_outputs_dir = f"{current_file_tests_dir}"
            platform = "codeforces"

            source_lang = "Java"
            if filename_parts[3] == "py":
                source_lang = "Python"

            if filename_parts[0].startswith("atcoder"):
                current_file_tests_dir = f"{avatar_test_cases_dir}/atcoder/{filename_parts[1]}/{filename_parts[2]}"
                current_file_inputs_dir = f"{current_file_tests_dir}/in"
                current_file_outputs_dir = f"{current_file_tests_dir}/out"
                platform = "atcoder"

            remove_extension(current_file_inputs_dir)
            remove_extension(current_file_outputs_dir)

            test_files = os.listdir(current_file_inputs_dir)

            for k in range(len(test_files)):
                inp_file = f"{current_file_inputs_dir}/{test_files[k]}"
                out_file = f"{current_file_outputs_dir}/{test_files[k]}"

                if platform == "codeforces":
                    if test_files[k].endswith("input"):
                        tmp_filename_parts = test_files[k].split("_")
                        inp_file = f"{current_file_inputs_dir}/{tmp_filename_parts[0]}_input"
                        out_file = f"{current_file_outputs_dir}/{tmp_filename_parts[0]}_output"
                    else:
                        continue

                with open(inp_file , 'r') as f:
                    f_in = f.read()
                with open(out_file , 'r') as f:
                    f_out = f.read()

                verdict, report, report_dict = compiler.test(current_code_dir, current_file, f_in, f_out, source_lang)
                
                if verdict == Constants.TEST_PASSED:
                    total_test_for_pl += 1
                    with open(f"{cleaned_test_case_dir}/{current_file_w_o_ext}_{k}.in", 'w') as output_file:
                        output_file.write(f_in)
                    with open(f"{cleaned_test_case_dir}/{current_file_w_o_ext}_{k}.out", 'w') as output_file:
                        output_file.write(f_out)

                else:
                    failed_test += 1
                    if verdict == Constants.COMPILATION_ERROR:
                        compilation_error_report[current_file] = report_dict
                        total_compilation_failed += 1
                    elif verdict == Constants.TEST_MISMATCH:
                        report_dict["Test_file"] = test_files[k]
                        test_mismatch_report[current_file] = report_dict
                        total_test_mismatch += 1
                    elif verdict == Constants.RUNTIME_ERROR:
                        runtime_error_report[current_file] = report_dict
                        total_runtime_failed += 1
                    elif verdict == Constants.INFINITE_LOOP:
                        inf_loop_report[current_file] = report_dict
                        total_inf_loop += 1
                    elif verdict == Constants.TOKEN_LIMIT:
                        token_limit_report.append(current_file)
                        total_token_limit += 1


        print(f"Total test for {avatar_pls[j]} - {total_test_for_pl}")
        print(f"Total Failed tests for {avatar_pls[j]} - {failed_test}")
        print(f"Total Compilation Error for {avatar_pls[j]} - {total_compilation_failed}")
        print(f"Total Runtime Error tests for {avatar_pls[j]} - {total_runtime_failed}")
        print(f"Total Mismatched tests for {avatar_pls[j]} - {total_test_mismatch}")
        print(f"Total Inf Loop tests for {avatar_pls[j]} - {total_inf_loop}")

        #remove all .class files generated
        dir_files = os.listdir(current_code_dir)
        for file in dir_files:
            if ".class" in file: os.remove(current_code_dir +"/"+ file)

        report_dir = f"./avatar_initial_test_cleanup" 
        compilation_error_report_fp = Path(report_dir).joinpath(f"avatar_ground_truths_errors_{avatar_pls[j]}.json")
        summary_report_fp = Path(report_dir).joinpath(f"avatar_ground_truths_summary_{avatar_pls[j]}.txt")

        os.makedirs(report_dir, exist_ok=True)
        with open(summary_report_fp, "w", encoding="utf-8") as report:
            report.writelines(f"Total test - {total_test_for_pl}\n")
            report.writelines(f"Total Failed tests - {failed_test}\n")
            report.writelines(f"Total Compilation Error - {total_compilation_failed}\n")
            report.writelines(f"Total Runtime Error tests - {total_runtime_failed}\n")
            report.writelines(f"Total Mismatched tests - {total_test_mismatch}\n")
            report.writelines(f"Total Inf Loop tests - {total_inf_loop}\n")

        with open(compilation_error_report_fp, "w", encoding="utf-8") as report:
            error_files = {'compile': compilation_error_report, 'runtime': runtime_error_report, 'inf_loop': inf_loop_report, 'test_mismatch': test_mismatch_report}
            json.dump(error_files, report)
            report.close()