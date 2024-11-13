import os
import shutil

debug_itr = 3
model = "gpt-4o-mini"

dataset = ["avatar", "codenet"]
dataset = ["evalplus"]
t_pls = ["C", "C++", "Go", "Java", "Python"]
t_pls = ["Java"]
debug_dir = f"repair/debug_on_translated_codes_itr"

for dt in dataset:
    s_pls = ["C", "C++", "Go", "Java", "Python"]
    s_pls = ["Python"]
    if dt == "avatar":
        s_pls = ["Java", "Python"]

    for sl in s_pls:
        for tl in t_pls:
            if not (sl == tl):
                report_dir = f"repair/combine_debug_results/{dt}/{sl}/{tl}"

                for k in range(debug_itr + 1):
                    if k == 0:
                        base_translation_dir = f"Generations/translation"
                    else:
                        base_translation_dir = f"{debug_dir}{k}"

                    temp_translation_dir = f"{base_translation_dir}/{dt}/{sl}/{tl}"
                    temp_translation_files = [f for f in os.listdir(temp_translation_dir) if f.split(".")[-1] in ["py", "java", "c", "cpp", "go", "c++"]]
                    iteration_response_dir = f"{debug_dir}{k+1}/{dt}/{sl}/{tl}"

                    if os.path.isdir(iteration_response_dir):
                        iteration_response_files = [f for f in os.listdir(iteration_response_dir) if f.split(".")[-1] in ["py", "java", "c", "cpp", "go", "c++"]]
                        previous_correct_files = list(set(temp_translation_files) - set(iteration_response_files))

                        print(f"itr - {k} -> For {dt}, {sl} -> {tl}, copying {len(previous_correct_files)} files from {temp_translation_dir}")

                        for file in previous_correct_files:
                            old_fp = f"{os.getcwd()}/{temp_translation_dir}/{file}"
                            new_dir = f"{os.getcwd()}/{report_dir}"
                            os.makedirs(new_dir, exist_ok=True)
                            shutil.copy(old_fp, f"{new_dir}/{file}")
                            
                    else:
                        previous_correct_files = temp_translation_files

                        print(f"itr - {k} -> For {dt}, {sl} -> {tl}, copying {len(previous_correct_files)} files from {temp_translation_dir}")

                        for file in previous_correct_files:
                            old_fp = f"{os.getcwd()}/{temp_translation_dir}/{file}"
                            new_dir = f"{os.getcwd()}/{report_dir}"
                            os.makedirs(new_dir, exist_ok=True)
                            shutil.copy(old_fp, f"{new_dir}/{file}")

                        break


                
