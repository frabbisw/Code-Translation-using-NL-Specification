import json
import os
import argparse
from pathlib import Path


def main(args):
    translation_dir = f"Generations/translation/evalplus/Python/Java"
    ordered_files = [f.split(".")[0] for f in os.listdir(translation_dir) if f.split(".")[-1] in ["java"]]
    #ordered_files = [x.strip() for x in open("evalplus_target_files.txt", "r").readlines()]
    os.makedirs(args.report_dir, exist_ok=True)
    compile_failed = []
    runtime_failed = []
    test_failed = []
    test_passed = []

    for f in ordered_files:
        fname = f + '.java'
        # print(f"Filename: {fname}")

        if os.path.exists(f'./EvalplusResults/on_base_translation/with_evaluation_test_cases/target/surefire-reports/com.example.{f}Test.txt'):
            with open(f'./EvalplusResults/on_base_translation/with_evaluation_test_cases/target/surefire-reports/com.example.{f}Test.txt', 'r') as report:
                content = report.read()
                if 'Errors: 0' not in content:
                    runtime_failed.append([fname, content])
                elif 'Errors: 0' in content and 'Failures: 0' in content:
                    test_passed.append([fname, content])
                else:
                    test_failed.append([fname, content])

        elif f in []: # infinite loop
            runtime_failed.append([fname, 'the program enters an infinite loop'])

        else:
            os.system(f'javac Generations/translation/evalplus/Python/Java/{fname} 2> compile_out_evalplus.txt')
            with open('compile_out_evalplus.txt', 'r') as report:
                compile_failed.append([fname, report.read()])
            
            os.remove('compile_out_evalplus.txt')

    json_fp = Path(args.report_dir).joinpath(f"evalplus_errors_from_{args.source_lang}_to_{args.target_lang}_{args.attempt}.json")
    with open(json_fp, "w", encoding="utf-8") as report:
        error_files = {'test passed' : test_passed, 'compile failed': compile_failed, 'runtime failed': runtime_failed, 'test mismatch': test_failed, 'no_of_correct' : len(test_passed), 'no_of_compile_fail' : len(compile_failed), 'no_of_runtime_fail' : len(runtime_failed), 'no_of_test_mismatch' : len(test_failed)}
        for i in range(len(test_failed)):
            print(test_failed[i][0])
        json.dump(error_files, report, indent=4)
        report.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='execute evalplus tests')
    parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--target_lang', help='target language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
    parser.add_argument('--report_dir', help='path to directory to store report', required=True, type=str)
    parser.add_argument('--attempt', help='attempt number', required=True, type=int)
    args = parser.parse_args()

    main(args)
