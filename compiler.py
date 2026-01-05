import subprocess
from subprocess import Popen, PIPE
import signal
import os
import Constants
import re
import shutil
from pathlib import Path

def compare_outputs(stdout: str, f_out: str, precision: int = 3) -> bool:
    def parse_and_round(s):
        tokens = re.split(r'(\s+)', s)  # Split while keeping whitespace
        return [
            round(float(token), precision) if re.fullmatch(r"-?\d+\.\d+", token) else token
            for token in tokens
        ]

    return parse_and_round(stdout) == parse_and_round(f_out)

def _test_java(java_code_file_dir, java_file_name, input_content, output_content):
    try:
        subprocess.run("javac "+ java_code_file_dir + "/" + java_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(java_code_file_dir + "/" + java_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, "", {}
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}", {"Compilation_Error": e.stderr.decode()}
        

    f_out = output_content
    p = Popen(['java', java_file_name.split(".")[0]], cwd=java_code_file_dir, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=30)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}", {"Inf_Loop_Info": stdout.decode()}
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}", {"Inf. Loop for Input": str(input_content)}
    try:
        if float(stdout.decode(errors="ignore"))%1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))
            f_out = str(int(float(f_out)))

        else:
            # find how many decimal points are there in the output
            stdout_temp = stdout.decode(errors="ignore").strip()
            f_out_temp = f_out.strip()
            f_out_total_dec_points = len(f_out_temp.split(".")[1])
            stdout_total_dec_points = len(stdout_temp.split(".")[1])
            min_dec_points = min(f_out_total_dec_points, stdout_total_dec_points)

            stdout = str(round(float(stdout.decode(errors="ignore")), min_dec_points))
            f_out = str(round(float(f_out), min_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")
        
    if(stdout.strip()==f_out.strip()):
        return Constants.TEST_PASSED, "", {}
    else:
        if compare_outputs(stdout.strip(), f_out.strip()):
            return Constants.TEST_PASSED, "", {}
        elif stderr_data.decode()=='':
            return Constants.TEST_MISMATCH, f"Input: {str(input_content)} Expected/Actual: {str(f_out)} Generated: {str(stdout)}", {"Actual": str(f_out), "Generated": str(stdout)}
        else:
            return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}", {"Error_Type": str(stderr_data.decode())}
        

def _test_python(python_code_file_dir, python_file_name, input_content, output_content):
    try:
        subprocess.run("python3 -m py_compile "+ python_code_file_dir + "/" + python_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(python_code_file_dir + "/" + python_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, "", {}
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}", {"Compilation_Error": e.stderr.decode()}
        
    f_out = output_content
    p = Popen(['python3', python_file_name], cwd=python_code_file_dir, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=30)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}", {"Inf_Loop_Info": stdout.decode()}
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}", {"Inf. Loop for Input": str(input_content)}
    try:
        if float(stdout.decode(errors="ignore"))%1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))
            f_out = str(int(float(f_out)))

        else:
            # find how many decimal points are there in the output
            stdout_temp = stdout.decode(errors="ignore").strip()
            f_out_temp = f_out.strip()
            f_out_total_dec_points = len(f_out_temp.split(".")[1])
            stdout_total_dec_points = len(stdout_temp.split(".")[1])
            min_dec_points = min(f_out_total_dec_points, stdout_total_dec_points)

            stdout = str(round(float(stdout.decode(errors="ignore")), min_dec_points))
            f_out = str(round(float(f_out), min_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")
        
    if(stdout.strip()==f_out.strip()):
        return Constants.TEST_PASSED, "", {}
    else:
        if compare_outputs(stdout.strip(), f_out.strip()):
            return Constants.TEST_PASSED, "", {}
        elif stderr_data.decode()=='':
            return Constants.TEST_MISMATCH, f"Input: {str(input_content)} Expected/Actual: {str(f_out)} Generated: {str(stdout)}", {"Actual": str(f_out), "Generated": str(stdout)}
        else:
            return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}", {"Error_Type": str(stderr_data.decode())}
        

def _test_c(c_code_file_dir, c_file_name, input_content, output_content):
    try:
        subprocess.run("gcc -o exec_output "+ c_code_file_dir + "/" + c_file_name + " -lm -lgmp", check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(c_code_file_dir + "/" + c_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, "", {}
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}", {"Compilation_Error": e.stderr.decode()}
        
    f_out = output_content
    p = Popen(['./exec_output'], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=5)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}", {"Inf_Loop_Info": stdout.decode()}
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}", {"Inf. Loop for Input": str(input_content)}
    try:
        if float(stdout.decode(errors="ignore"))%1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))
            f_out = str(int(float(f_out)))

        else:
            # find how many decimal points are there in the output
            stdout_temp = stdout.decode(errors="ignore").strip()
            f_out_temp = f_out.strip()
            f_out_total_dec_points = len(f_out_temp.split(".")[1])
            stdout_total_dec_points = len(stdout_temp.split(".")[1])
            min_dec_points = min(f_out_total_dec_points, stdout_total_dec_points)

            stdout = str(round(float(stdout.decode(errors="ignore")), min_dec_points))
            f_out = str(round(float(f_out), min_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")
        
    if(stdout.strip()==f_out.strip()):
        return Constants.TEST_PASSED, "", {}
    else:
        if compare_outputs(stdout.strip(), f_out.strip()):
            return Constants.TEST_PASSED, "", {}
        elif stderr_data.decode()=='':
            return Constants.TEST_MISMATCH, f"Input: {str(input_content)} Expected/Actual: {str(f_out)} Generated: {str(stdout)}", {"Actual": str(f_out), "Generated": str(stdout)}
        else:
            return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}", {"Error_Type": str(stderr_data.decode())}
        

def _test_cpp(cpp_code_file_dir, cpp_file_name, input_content, output_content):
    try:
        subprocess.run("g++ -o exec_output -std=c++11 "+ cpp_code_file_dir + "/" + cpp_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(cpp_code_file_dir + "/" + cpp_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, "", {}
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}", {"Compilation_Error": e.stderr.decode()}
        
    f_out = output_content
    p = Popen(['./exec_output'], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=5)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}", {"Inf_Loop_Info": stdout.decode()}
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}", {"Inf. Loop for Input": str(input_content)}
    try:
        if float(stdout.decode(errors="ignore"))%1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))
            f_out = str(int(float(f_out)))

        else:
            # find how many decimal points are there in the output
            stdout_temp = stdout.decode(errors="ignore").strip()
            f_out_temp = f_out.strip()
            f_out_total_dec_points = len(f_out_temp.split(".")[1])
            stdout_total_dec_points = len(stdout_temp.split(".")[1])
            min_dec_points = min(f_out_total_dec_points, stdout_total_dec_points)

            stdout = str(round(float(stdout.decode(errors="ignore")), min_dec_points))
            f_out = str(round(float(f_out), min_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")
        
    if(stdout.strip()==f_out.strip()):
        return Constants.TEST_PASSED, "", {}
    else:
        if compare_outputs(stdout.strip(), f_out.strip()):
            return Constants.TEST_PASSED, "", {}
        elif stderr_data.decode()=='':
            return Constants.TEST_MISMATCH, f"Input: {str(input_content)} Expected/Actual: {str(f_out)} Generated: {str(stdout)}", {"Actual": str(f_out), "Generated": str(stdout)}
        else:
            return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}", {"Error_Type": str(stderr_data.decode())}
        

def _test_go(go_code_file_dir, go_file_name, input_content, output_content):
    try:
        subprocess.run("go build -o exec_output "+ go_code_file_dir + "/" + go_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(go_code_file_dir + "/" + go_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, "", {}
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}", {"Compilation_Error": e.stderr.decode()}
        
    f_out = output_content
    p = Popen(["./exec_output"], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=30)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}", {"Inf_Loop_Info": stdout.decode()}
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}", {"Inf. Loop for Input": str(input_content)}
    try:
        if float(stdout.decode(errors="ignore"))%1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))
            f_out = str(int(float(f_out)))

        else:
            # find how many decimal points are there in the output
            stdout_temp = stdout.decode(errors="ignore").strip()
            f_out_temp = f_out.strip()
            f_out_total_dec_points = len(f_out_temp.split(".")[1])
            stdout_total_dec_points = len(stdout_temp.split(".")[1])
            min_dec_points = min(f_out_total_dec_points, stdout_total_dec_points)

            stdout = str(round(float(stdout.decode(errors="ignore")), min_dec_points))
            f_out = str(round(float(f_out), min_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")
        
    if(stdout.strip()==f_out.strip()):
        return Constants.TEST_PASSED, "", {}
    else:
        if compare_outputs(stdout.strip(), f_out.strip()):
            return Constants.TEST_PASSED, "", {}
        elif stderr_data.decode()=='':
            return Constants.TEST_MISMATCH, f"Input: {str(input_content)} Expected/Actual: {str(f_out)} Generated: {str(stdout)}", {"Actual": str(f_out), "Generated": str(stdout)}
        else:
            return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}", {"Error_Type": str(stderr_data.decode())}
        

def _test_javascript(js_code_file_dir, js_file_name, input_content, output_content):
    try:
        subprocess.run(
            f"node --check {js_code_file_dir}/{js_file_name}",
            check=True,
            capture_output=True,
            shell=True,
            timeout=100
        )
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(js_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, "", {}
        else:
            return (
                Constants.COMPILATION_ERROR,
                f"Compilation_Error: {e.stderr.decode()}",
                {"Compilation_Error": e.stderr.decode()}
            )

    f_out = output_content
    p = Popen(
        ['node', js_file_name],
        cwd=js_code_file_dir,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE
    )

    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=30)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, stdout.decode(), {"Inf_Loop_Info": stdout.decode()}
        except subprocess.TimeoutExpired:
            return (
                Constants.INFINITE_LOOP,
                f"Inf. Loop for Input: {str(input_content)}",
                {"Inf. Loop for Input": str(input_content)}
            )

    try:
        if float(stdout.decode(errors="ignore")) % 1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))
            f_out = str(int(float(f_out)))
        else:
            stdout_temp = stdout.decode(errors="ignore").strip()
            f_out_temp = f_out.strip()
            min_dec_points = min(
                len(stdout_temp.split(".")[1]),
                len(f_out_temp.split(".")[1])
            )
            stdout = str(round(float(stdout_temp), min_dec_points))
            f_out = str(round(float(f_out), min_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")

    if stdout.strip() == f_out.strip():
        return Constants.TEST_PASSED, "", {}
    else:
        if compare_outputs(stdout.strip(), f_out.strip()):
            return Constants.TEST_PASSED, "", {}
        elif stderr_data.decode() == "":
            return (
                Constants.TEST_MISMATCH,
                f"Input: {str(input_content)} Expected/Actual: {str(f_out)} Generated: {str(stdout)}",
                {"Actual": str(f_out), "Generated": str(stdout)}
            )
        else:
            return (
                Constants.RUNTIME_ERROR,
                f"Error_Type: {stderr_data.decode()}",
                {"Error_Type": stderr_data.decode()}
            )


def _test_rust(rust_code_file_dir, rust_file_name, input_content, output_content):
    try:
        subprocess.run(
            f"rustc {rust_code_file_dir}/{rust_file_name} -O -o exec_output",
            check=True,
            capture_output=True,
            shell=True,
            timeout=100
        )
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(rust_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, "", {}
        else:
            return (
                Constants.COMPILATION_ERROR,
                f"Compilation_Error: {e.stderr.decode()}",
                {"Compilation_Error": e.stderr.decode()}
            )

    f_out = output_content
    p = Popen(
        ['./exec_output'],
        cwd=os.getcwd(),
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE
    )

    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=5)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, stdout.decode(), {"Inf_Loop_Info": stdout.decode()}
        except subprocess.TimeoutExpired:
            return (
                Constants.INFINITE_LOOP,
                f"Inf. Loop for Input: {str(input_content)}",
                {"Inf. Loop for Input": str(input_content)}
            )

    try:
        if float(stdout.decode(errors="ignore")) % 1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))
            f_out = str(int(float(f_out)))
        else:
            stdout_temp = stdout.decode(errors="ignore").strip()
            f_out_temp = f_out.strip()
            min_dec_points = min(
                len(stdout_temp.split(".")[1]),
                len(f_out_temp.split(".")[1])
            )
            stdout = str(round(float(stdout_temp), min_dec_points))
            f_out = str(round(float(f_out), min_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")

    if stdout.strip() == f_out.strip():
        return Constants.TEST_PASSED, "", {}
    else:
        if compare_outputs(stdout.strip(), f_out.strip()):
            return Constants.TEST_PASSED, "", {}
        elif stderr_data.decode() == "":
            return (
                Constants.TEST_MISMATCH,
                f"Input: {str(input_content)} Expected/Actual: {str(f_out)} Generated: {str(stdout)}",
                {"Actual": str(f_out), "Generated": str(stdout)}
            )
        else:
            return (
                Constants.RUNTIME_ERROR,
                f"Error_Type: {stderr_data.decode()}",
                {"Error_Type": stderr_data.decode()}
            )


def test(code_file_dir, file_name, input_content, output_content, source_lang):
    if source_lang == "Python":
        return _test_python(code_file_dir, file_name, input_content, output_content)
    elif source_lang == "Java":
        return _test_java(code_file_dir, file_name, input_content, output_content)
    elif source_lang == "C":
        return _test_c(code_file_dir, file_name, input_content, output_content)
    elif source_lang == "C++":
        return _test_cpp(code_file_dir, file_name, input_content, output_content)
    elif source_lang == "Go":
        return _test_go(code_file_dir, file_name, input_content, output_content)
    elif source_lang == "Javascript":
        return _test_javascript(code_file_dir, file_name, input_content, output_content)
    elif source_lang == "Rust":
        return _test_rust(code_file_dir, file_name, input_content, output_content)
    

def _output_java(java_code_file_dir, java_file_name, input_content):
    try:
        subprocess.run("javac "+ java_code_file_dir + "/" + java_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(java_code_file_dir + "/" + java_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"
        
    p = Popen(['java', java_file_name.split(".")[0]], cwd=java_code_file_dir, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=30)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}"
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}"
        
    try:
        if float(stdout.decode(errors="ignore"))%1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))

        else:
            # find how many decimal points are there in the output
            stdout_temp = stdout.decode(errors="ignore").strip()
            stdout_total_dec_points = len(stdout_temp.split(".")[1])

            stdout = str(round(float(stdout.decode(errors="ignore")), stdout_total_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")
    
    if stderr_data.decode()=='':
        return Constants.OUTPUT_GENERATED, str(stdout)
    else:
        return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}"
    

def _output_python(python_code_file_dir, python_file_name, input_content):
    try:
        subprocess.run("python3 -m py_compile "+ python_code_file_dir + "/" + python_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(python_code_file_dir + "/" + python_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"

    p = Popen(['python3', python_file_name], cwd=python_code_file_dir, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=30)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}"
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}"
        
    try:
        if float(stdout.decode(errors="ignore"))%1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))

        else:
            # find how many decimal points are there in the output
            stdout_temp = stdout.decode(errors="ignore").strip()
            stdout_total_dec_points = len(stdout_temp.split(".")[1])

            stdout = str(round(float(stdout.decode(errors="ignore")), stdout_total_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")
        
    if stderr_data.decode()=='':
        return Constants.OUTPUT_GENERATED, str(stdout)
    else:
        return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}"
    

def _output_c(c_code_file_dir, c_file_name, input_content):
    try:
        subprocess.run("gcc -o exec_output "+ c_code_file_dir + "/" + c_file_name + " -lm -lgmp", check=True, capture_output=True, shell=True, timeout=10)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(c_code_file_dir + "/" + c_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"
    
    p = Popen(['./exec_output'], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=5)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}"
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}"
        
    try:
        if float(stdout.decode(errors="ignore"))%1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))

        else:
            # find how many decimal points are there in the output
            stdout_temp = stdout.decode(errors="ignore").strip()
            stdout_total_dec_points = len(stdout_temp.split(".")[1])

            stdout = str(round(float(stdout.decode(errors="ignore")), stdout_total_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")
    
    if stderr_data.decode()=='':
        return Constants.OUTPUT_GENERATED, str(stdout)
    else:
        return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}"
    

def _output_cpp(cpp_code_file_dir, cpp_file_name, input_content):
    try:
        subprocess.run("g++ -o exec_output -std=c++11 "+ cpp_code_file_dir + "/" + cpp_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(cpp_code_file_dir + "/" + cpp_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"
    
    p = Popen(['./exec_output'], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=30)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}"
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}"
        
    try:
        if float(stdout.decode(errors="ignore"))%1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))

        else:
            # find how many decimal points are there in the output
            stdout_temp = stdout.decode(errors="ignore").strip()
            stdout_total_dec_points = len(stdout_temp.split(".")[1])

            stdout = str(round(float(stdout.decode(errors="ignore")), stdout_total_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")
    
    if stderr_data.decode()=='':
        return Constants.OUTPUT_GENERATED, str(stdout)
    else:
        return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}"
    

def _output_go(go_code_file_dir, go_file_name, input_content):
    try:
        subprocess.run("go build -o exec_output "+ go_code_file_dir + "/" + go_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(go_code_file_dir + "/" + go_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"
    
    p = Popen(["./exec_output"], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=30)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}"
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}"
    
    try:
        if float(stdout.decode(errors="ignore"))%1 == 0:
            stdout = str(int(float(stdout.decode(errors="ignore"))))

        else:
            # find how many decimal points are there in the output
            stdout_temp = stdout.decode(errors="ignore").strip()
            stdout_total_dec_points = len(stdout_temp.split(".")[1])

            stdout = str(round(float(stdout.decode(errors="ignore")), stdout_total_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")
    
    if stderr_data.decode()=='':
        return Constants.OUTPUT_GENERATED, str(stdout)
    else:
        return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}"
    

def _output_javascript(js_code_file_dir, js_file_name, input_content):
    # Syntax check (closest to "compilation" for JS)
    try:
        subprocess.run(
            "node --check " + js_code_file_dir + "/" + js_file_name,
            check=True,
            capture_output=True,
            shell=True,
            timeout=100
        )
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(js_code_file_dir + "/" + js_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"

    # Run
    p = Popen(
        ['node', js_file_name],
        cwd=js_code_file_dir,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE
    )
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=30)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}"
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}"

    # Normalize numeric output (same pattern as your Java)
    try:
        out_str = stdout.decode(errors="ignore")
        if float(out_str) % 1 == 0:
            stdout = str(int(float(out_str)))
        else:
            stdout_temp = out_str.strip()
            stdout_total_dec_points = len(stdout_temp.split(".")[1])
            stdout = str(round(float(out_str), stdout_total_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")

    # Return
    if stderr_data.decode() == '':
        return Constants.OUTPUT_GENERATED, str(stdout)
    else:
        return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}"


def _output_rust(rust_code_file_dir, rust_file_name, input_content):
    # Compile
    try:
        subprocess.run(
            "rustc " + rust_code_file_dir + "/" + rust_file_name + " -O -o exec_output",
            check=True,
            capture_output=True,
            shell=True,
            timeout=100
        )
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(rust_code_file_dir + "/" + rust_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"

    # Run binary
    p = Popen(
        ['./exec_output'],
        cwd=os.getcwd(),   # binary is in this dir (matches your pattern)
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE
    )
    try:
        stdout, stderr_data = p.communicate(input=input_content.encode(), timeout=30)
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGINT)
        try:
            stdout, stderr_data = p.communicate(timeout=5)
            return Constants.INFINITE_LOOP, f"{stdout.decode()}"
        except subprocess.TimeoutExpired:
            return Constants.INFINITE_LOOP, f"Inf. Loop for Input: {str(input_content)}"

    # Normalize numeric output (same pattern as your Java)
    try:
        out_str = stdout.decode(errors="ignore")
        if float(out_str) % 1 == 0:
            stdout = str(int(float(out_str)))
        else:
            stdout_temp = out_str.strip()
            stdout_total_dec_points = len(stdout_temp.split(".")[1])
            stdout = str(round(float(out_str), stdout_total_dec_points))
    except:
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="ignore")

    # Return
    if stderr_data.decode() == '':
        return Constants.OUTPUT_GENERATED, str(stdout)
    else:
        return Constants.RUNTIME_ERROR, f"Error_Type: {str(stderr_data.decode())}"


def get_output(code_file_dir, file_name, input_content, source_lang):
    if source_lang == "Python":
        return _output_python(code_file_dir, file_name, input_content)
    elif source_lang == "Java":
        return _output_java(code_file_dir, file_name, input_content)
    elif source_lang == "C":
        return _output_c(code_file_dir, file_name, input_content)
    elif source_lang == "C++":
        return _output_cpp(code_file_dir, file_name, input_content)
    elif source_lang == "Go":
        return _output_go(code_file_dir, file_name, input_content)
    elif source_lang == "Javascript":
        return _output_javascript(code_file_dir, file_name, input_content)
    elif source_lang == "Rust":
        return _output_rust(code_file_dir, file_name, input_content)
    

def _compile_java(java_code_file_dir, java_file_name):
    try:
        subprocess.run("javac "+ java_code_file_dir + "/" + java_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(java_code_file_dir + "/" + java_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"
        
    return Constants.COMPILATION_SUCCESS, ""
    

def _compile_python(python_code_file_dir, python_file_name):
    try:
        subprocess.run("python3 -m py_compile "+ python_code_file_dir + "/" + python_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(python_code_file_dir + "/" + python_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"

    return Constants.COMPILATION_SUCCESS, ""
    

def _compile_c(c_code_file_dir, c_file_name):
    try:
        subprocess.run("gcc -c "+ c_code_file_dir + "/" + c_file_name + " -lm -lgmp", check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(c_code_file_dir + "/" + c_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"
    
    return Constants.COMPILATION_SUCCESS, ""
    

def _compile_cpp(cpp_code_file_dir, cpp_file_name):
    try:
        subprocess.run("g++ -c -std=c++11 "+ cpp_code_file_dir + "/" + cpp_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(cpp_code_file_dir + "/" + cpp_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"
    
    return Constants.COMPILATION_SUCCESS, ""
    

def _compile_go(go_code_file_dir, go_file_name):
    try:
        subprocess.run("go build -o exec_output "+ go_code_file_dir + "/" + go_file_name, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(go_code_file_dir + "/" + go_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"
    
    return Constants.COMPILATION_SUCCESS, ""


def _compile_javascript(js_code_file_dir, js_file_name):
    try:
        subprocess.run(
            "node --check " + js_code_file_dir + "/" + js_file_name,
            check=True,
            capture_output=True,
            shell=True,
            timeout=100
        )
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(js_code_file_dir + "/" + js_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"

    return Constants.COMPILATION_SUCCESS, ""


def _compile_rust(rust_code_file_dir, rust_file_name):
    try:
        subprocess.run(
            "rustc " + rust_code_file_dir + "/" + rust_file_name + " -O -o exec_output",
            check=True,
            capture_output=True,
            shell=True,
            timeout=100
        )
    except subprocess.CalledProcessError as e:
        if '# Token size exceeded.' in open(rust_code_file_dir + "/" + rust_file_name, 'r').read():
            return Constants.TOKEN_LIMIT, ""
        else:
            return Constants.COMPILATION_ERROR, f"Compilation_Error: {e.stderr.decode()}"

    return Constants.COMPILATION_SUCCESS, ""



def compile(code_file_dir, file_name, source_lang):
    if source_lang == "Python":
        return _compile_python(code_file_dir, file_name)
    elif source_lang == "Java":
        return _compile_java(code_file_dir, file_name)
    elif source_lang == "C":
        return _compile_c(code_file_dir, file_name)
    elif source_lang == "C++":
        return _compile_cpp(code_file_dir, file_name)
    elif source_lang == "Go":
        return _compile_go(code_file_dir, file_name)
    elif source_lang == "Javascript":
        return _compile_javascript(code_file_dir, file_name)
    elif source_lang == "Rust":
        return _compile_rust(code_file_dir, file_name)
    

def compile_junit(jar_location, source_files):
    junit_jar = f"{jar_location}/junit-4.13.2.jar"
    hamcrest_jar = f"{jar_location}/hamcrest-core-1.3.jar"
    temp_dir = f"{os.getcwd()}"

    for file in source_files:
        src = Path(file).resolve()
        dst = (Path(temp_dir) / src.name).resolve()

        if src == dst:
            continue
        shutil.copy(file, temp_dir)

    compile_cmd = f"javac -cp {junit_jar}:{hamcrest_jar}"

    for file in source_files:
        compile_cmd = compile_cmd + f" {str(Path(file).name)}"

    try:
        subprocess.run(compile_cmd, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        return Constants.COMPILATION_ERROR, e.stderr.decode()

    return Constants.COMPILATION_SUCCESS, None


def run_junit(jar_location, source_files, test_file):
    junit_jar = f"{jar_location}/junit-4.13.2.jar"
    hamcrest_jar = f"{jar_location}/hamcrest-core-1.3.jar"
    temp_dir = os.getcwd()

    for file in source_files:
        src = Path(file).resolve()
        dst = (Path(temp_dir) / src.name).resolve()

        if src == dst:
            continue
        shutil.copy(file, temp_dir)

    compile_cmd = f"javac -cp {junit_jar}:{hamcrest_jar}"

    for file in source_files:
        compile_cmd = compile_cmd + f" {str(Path(file).name)}"

    try:
        subprocess.run(compile_cmd, check=True, capture_output=True, shell=True, timeout=100)
    except subprocess.CalledProcessError as e:
        print("==============================", e.stderr.decode(), "==============================", e.stdout.decode(), "==============================")
    run_cmd = f"java -cp {junit_jar}:{hamcrest_jar}:{temp_dir} org.junit.runner.JUnitCore {str(Path(test_file).stem)}"
    try:
        result = subprocess.run(run_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, shell=True, timeout=20)
    except subprocess.CalledProcessError as e:
        out = (e.stdout or b"") + b"\n" + (e.stderr or b"")
        text = out.decode(errors="replace")
        if "java.lang.AssertionError" in text:
            return Constants.TEST_MISMATCH, text
        else:
            return Constants.RUNTIME_ERROR, text
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"") + b"\n" + (e.stderr or b"")
        return Constants.INFINITE_LOOP, out.decode(errors="replace")

    return Constants.TEST_PASSED, result.stdout.decode()