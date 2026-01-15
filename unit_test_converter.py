from pathlib import Path
import re
from fuzzywuzzy import fuzz
import ast
import time
import os
import re
from pathlib import Path
from subprocess import Popen, PIPE
import utility

def load_source_content(source_file):
    content = None
    with open(source_file, "r") as f:
        content = f.read()
        f.close()
    return content

def load_source_content_arr(source_file):
    content = None
    with open(source_file, "r") as f:
        content = f.readlines()
        f.close()
    return content

def wait_for_file(filepath, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(filepath):
            return True
        time.sleep(0.1)
    return False

def get_single_test(tests_str: str, test_name: str):
    for line in tests_str.splitlines():
        line = line.strip()
        if line.startswith(f"{test_name}:"):
            return line
    return None

def get_test_details(test):
    regex = r"(\w+):\s+self\.(\w+)\((.+?),\s+(\w+)\((.*)\)\)"
    match = re.match(regex, test)
    error = False
    if match:
        test_name = match.group(1)          # test_0
        assert_method = match.group(2)      # assertEqual
        expected_output = match.group(3)    # 0.0
        test_func = match.group(4)          # truncate_number
        func_input = match.group(5)         # 1000000000.0
    else:
        error = True

    dict = {}

    if error:
        return False, {}
    else:
        dict["test_name"] = test_name
        dict["assert_method"] = f"self.{assert_method}"
        dict["expected_output"] = expected_output
        dict["test_func"] = test_func
        dict["func_input"] = func_input
        return True, dict
    
def run_files_to_generate_testfiles(source_file):
    code_id = Path(source_file).stem
    if code_id == "__pycache__" or code_id == "__init__" or code_id.endswith("temp") or Path(source_file).name.endswith(".class"):
        return
        
    Popen(['python3', source_file], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)

JAVA_FLOAT_MAX = 3.4028235e38
JAVA_DOUBLE_MAX = 1.7976931348623157E308
JAVA_INT_MAX = 2147483647
JAVA_LONG_MAX = 9223372036854775807

def determine_python_list_elaborately(str_input):
    try:
        parsed_list = ast.literal_eval(str_input)

        if isinstance(parsed_list, list):
            if not parsed_list:
                return "list"
                
            if all(isinstance(elem, list) for elem in parsed_list):
                if all(all(isinstance(sub_elem, (int)) for sub_elem in elem) for elem in parsed_list):
                    return "list[list[int]]"
                if all(all(isinstance(sub_elem, (int, float)) for sub_elem in elem) for elem in parsed_list):
                    return "list[list[float]]"
                return "list[list[object]]"
            
            elif all(isinstance(elem, int) for elem in parsed_list):
                return "list[int]"
                
            elif all(isinstance(elem, float) for elem in parsed_list):
                return "list[float]"
            
            elif all(isinstance(elem, (int, float)) for elem in parsed_list) and any(isinstance(elem, float) for elem in parsed_list):
                return "list[float]"
            
            elif all(isinstance(elem, (str)) for elem in parsed_list):
                return "list[str]"
            
            else:
                return "list[object]"
        
    except (ValueError, SyntaxError):
        return "Unknown"
        
def convert_python_int_float_to_java_double(input):
    if "." in input or "e" in input:
        return input.strip()
    else:
        return input + ".0"
        
def convert_python_str_to_java_String(input):
    inp = str(input).strip()
    if inp.startswith("'") and inp.endswith("'") and len(str(inp)) > 2:
        s = inp[1:(len(inp) - 1)]
        s = s.replace("\\", "\\\\")
        return "\"" + s + "\""
    elif inp.startswith("'") and inp.endswith("'"):
        return "\"\""
    else:
        return inp
    
def convert_python_str_to_java_Char_Array(input):
    inp = str(input).strip()
    if inp.startswith("'") and inp.endswith("'") and len(str(inp)) == 3:
        return "'" + inp[1:(len(inp) - 1)] + "'"
    else:
        return inp
        
def split_params(param_string):
    # Regular expression to split on commas outside of angle brackets
    param_pattern = r',\s*(?![^<]*>)'
    return re.split(param_pattern, param_string)
    
def extract_type_and_name(param):
    # Match type and name including array brackets attached to the name
    match = re.match(r'(.+?)\s+(\w+(\[\])*)$', param.strip())
    if match:
        raw_type = match.group(1)
        name = match.group(2)

        # If the name has [] in it, move it to the type
        array_part = ''
        while name.endswith('[]'):
            name = name[:-2]
            array_part += '[]'
        final_type = raw_type + array_part
        return final_type.strip(), name.strip()
    return None, None
    
def remove_comments(java_code):
    # Remove single-line comments (//...)
    java_code = re.sub(r'//.*', '', java_code)
    # Remove multi-line comments (/*...*/)
    java_code = re.sub(r'/\*.*?\*/', '', java_code, flags=re.DOTALL)
    return java_code

def extract_method_signatures(java_file_path):
    # Read the Java file
    if wait_for_file(java_file_path, timeout=10):
        with open(java_file_path, 'r') as file:
            java_code = file.read()
            file.close()

    java_code = remove_comments(java_code)
    
    # Regular expression to match method names and parameters
    method_pattern = r'\b(?:public|private|protected)?\s*(?:static|final|synchronized)?\s*(?:<[\w\s,]+>\s*)?([\w<>\[\],\s]+(?:\.\w+)?(?:<.*?>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{'
    # method_pattern = r'\b(?:public|private|protected|static|final|synchronized)?\s*(?:<[\w\s,]+>\s*)?([\w<>\[\],\s]+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
    
    # Find all method signatures
    method_signatures = re.findall(method_pattern, java_code)
    
    methods_with_params = []
    
    for return_type, method_name, param_string in method_signatures:
        # Split the parameters by commas, ignore empty strings
        params = split_params(param_string)
        # Further split each parameter into type and name
        param_details = []
        for param in params:
            param_type, param_name = extract_type_and_name(param)
            if param_type and param_name:
                param_details.append((param_name, param_type))
        
        # Store method with its parameters
        try:
            methods_with_params.append({
                'method_name': method_name,
                'parameters': param_details,
                'return' : return_type
            })
        except:
            print(f"java_file_path -> {java_file_path}")
    return methods_with_params

def get_first_list_and_other_part_from_python_str(input_str):
    count = 1
    i = 0
    for i in range(1, len(input_str), 1):
        temp_char = input_str[i]
        if temp_char == "[":
            count += 1
        elif temp_char == "]":
            count -= 1

        if count == 0:
            break
        
    first_list = input_str[:(i + 1)]
    other_part = input_str[len(first_list):].strip()

    if other_part.startswith(","):
        other_part = other_part[1:].strip()

    return first_list,  other_part

def convert_to_java(func_name, func_input, func_output, test_name, params, translated_fp, code_id):
    might_overflow = False
    func_input_copy = func_input
    test_str = "\t@Test\n\tpublic void " + test_name + "() {\n"
    no_of_param = len(params)
    methods_with_param = extract_method_signatures(translated_fp)

    func_name_java = ""
    param_detail_java = []
    java_ret_type = ""
    max_similarity = 0
    for j in range(len(methods_with_param)):
        method_with_param = methods_with_param[j]
        method_name_java = method_with_param["method_name"]
        similarity = fuzz.ratio(func_name.replace("_", "").lower(), method_name_java.lower())
        if similarity > max_similarity:
            func_name_java = method_name_java
            param_detail_java = method_with_param["parameters"]
            java_ret_type = method_with_param["return"]
            max_similarity = similarity

    inp_sentence = ""
    out_sentence = ""
    assert_inps = ""
    incompatible_error = False
    custom_error_message = ""
    for i in range(no_of_param):
        if i != no_of_param - 1:
            param_name_python = params[i][0]
            param_type_python = ""
            if params[i][1] == "list[list]":
                param_type_python = "list[list]"
                param_value_python, func_input_copy = get_first_list_and_other_part_from_python_str(func_input_copy)

            elif func_input_copy.startswith("{"):
                param_type_python = "dict"
                param_value_python = func_input_copy.strip().split("}", 1)[0].strip() + "}"
                if len(func_input_copy.strip().split("}", 1)) > 1:
                    func_input_copy = func_input_copy.strip().split("}", 1)[1].strip()
                else:
                    func_input_copy = ""
                if func_input_copy.startswith(","): func_input_copy = func_input_copy[1:].strip()

            elif func_input_copy.startswith("["):
                param_type_python = "list"
                param_value_python, func_input_copy = get_first_list_and_other_part_from_python_str(func_input_copy)
                param_type_python = determine_python_list_elaborately(param_value_python)

            elif func_input_copy.startswith("("):
                param_type_python = "tuple"
                param_value_python = func_input_copy.strip().split(")", 1)[0].strip() + ")"
                if len(func_input_copy.strip().split(")", 1)) > 1:
                    func_input_copy = func_input_copy.strip().split(")", 1)[1].strip()
                else:
                    func_input_copy = ""
                if func_input_copy.startswith(","): func_input_copy = func_input_copy[1:].strip()

            elif func_input_copy.startswith("\""):
                param_type_python = "str"
                split_point = func_input_copy.find("\"", 1)
                param_value_python = func_input_copy[:split_point] + "\""
                func_input_copy = func_input_copy[split_point:]
                if len(func_input_copy.strip()) > 1:
                    func_input_copy = func_input_copy.strip()[1:]
                else:
                    func_input_copy = ""
                if func_input_copy.startswith(","): func_input_copy = func_input_copy[1:].strip()

            elif func_input_copy.startswith("'"):
                param_type_python = "str"
                split_point = func_input_copy.find("'", 1)
                param_value_python = func_input_copy[:split_point] + "'"
                func_input_copy = func_input_copy[split_point:]
                if len(func_input_copy.strip()) > 1:
                    func_input_copy = func_input_copy.strip()
                    func_input_copy = func_input_copy[1:].strip()
                else:
                    func_input_copy = ""
                if func_input_copy.startswith(","): func_input_copy = func_input_copy[1:].strip()

            else:
                param_value_python = func_input_copy.strip().split(",", 1)[0].strip()

                if len(func_input_copy.strip().split(",", 1)) > 1:
                    func_input_copy = func_input_copy.strip().split(",", 1)[1].strip()
                else:
                    func_input_copy = ""

                if param_value_python == "False" or param_value_python == "True":
                    param_type_python = "bool"
                elif "." in param_value_python:
                    param_type_python = "float"
                else:
                    param_type_python = "int"

            if param_type_python == "float":
                if param_value_python == "math.inf": param_value_python = JAVA_DOUBLE_MAX
                param_value_java = f"{param_value_python}"
                try:
                    if abs(float(param_value_python)) >= JAVA_FLOAT_MAX:
                        might_overflow = True
                except:
                    pass
                if param_detail_java[i][1] == "float":
                    inp_sentence = inp_sentence + "\t\tfloat " + param_name_python + " = " + param_value_java + "F;\n"
                elif param_detail_java[i][1] == "double":
                    inp_sentence = inp_sentence + "\t\tdouble " + param_name_python + " = " + param_value_java + ";\n"
                elif param_detail_java[i][1] == "Object":
                    inp_sentence = inp_sentence + "\t\tObject " + param_name_python + " = new Double(" + param_value_java + ");\n"
                else:
                    incompatible_error = True
                    java_error_param_type = param_detail_java[i][1]
                    java_error_param_name = param_detail_java[i][0]
                    custom_error_message = f"Python func: {func_name}() accepts {param_type_python}, whereas Java func: {func_name_java}() accepts {java_error_param_type} for variable {java_error_param_name}; using Object type appropriately so that Java function can support multiple types might solve this issue"
                assert_inps = assert_inps + param_name_python + ", "

            elif param_type_python == "int":
                param_value_java = f"{param_value_python}"
                try:
                    if abs(float(param_value_python)) >= JAVA_INT_MAX:
                        might_overflow = True
                except:
                    pass
                if param_detail_java[i][1] == "int":
                    inp_sentence = inp_sentence + "\t\tint " + param_name_python + " = " + param_value_java + ";\n"
                elif param_detail_java[i][1] == "long":
                    inp_sentence = inp_sentence + "\t\tlong " + param_name_python + " = " + param_value_java + ";\n"
                elif param_detail_java[i][1] == "double":
                    inp_sentence = inp_sentence + "\t\tdouble " + param_name_python + " = " + param_value_java + ";\n"
                elif param_detail_java[i][1] == "Object":
                    inp_sentence = inp_sentence + "\t\tObject " + param_name_python + " = new Integer(" + param_value_java + ");\n"
                assert_inps = assert_inps + param_name_python + ", "

            elif param_type_python == "bool":
                param_value_java = f"{param_value_python.lower()}"
                if param_detail_java[i][1] == "Object":
                    inp_sentence = inp_sentence + "\t\tObject " + param_name_python + " = new Boolean(" + param_value_java.lower() + ");\n"
                else:
                    inp_sentence = inp_sentence + "\t\tboolean " + param_name_python + " = " + param_value_java + ";\n"
                assert_inps = assert_inps + param_name_python + ", "

            elif param_type_python == "str":
                param_value_java = param_value_python.replace("'", "").replace("\"","").replace("\\", "\\\\")
                if param_detail_java[i][1] == "Object":
                    inp_sentence = inp_sentence + "\t\tObject " + param_name_python + " = new String(\"" + param_value_java + "\");\n"
                else:
                    inp_sentence = inp_sentence + "\t\tString " + param_name_python + " = " + "\"" + param_value_java + "\"" + ";\n"
                assert_inps = assert_inps + param_name_python + ", "

            elif param_type_python == "list[float]":
                if param_detail_java[i][1] == "List<Object>":
                    param_value_python = ast.literal_eval(param_value_python)
                    param_value_java = ""
                    for elem_idx in range(len(param_value_python)):
                        element = param_value_python[elem_idx]
                        if type(element) == type(1):
                            try:
                                if abs(float(element)) >= JAVA_INT_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type(1.1):
                            try:
                                if abs(float(element)) >= JAVA_DOUBLE_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type("a"):
                            element = "\"" + element + "\""
                        elif type(element) == type(None):
                            element = "null"
                        elif type(element) == type(True):
                            if element == False:
                                element = str(0)
                            else:
                                element = str(1)
                        elif type(element) == type([]):
                            var_name = "__temp_arr" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tObject[] " + var_name + " = {"
                            for elem_idx2 in range(len(element)):
                                if elem_idx2 != len(element) - 1:
                                    inp_sentence = inp_sentence + element[elem_idx2] + ", "
                                else:
                                    inp_sentence = inp_sentence + element[elem_idx2]
                            inp_sentence = inp_sentence + "};\n"
                            element = var_name
                        elif type(element) == type({}):
                            var_name = "__temp_dict" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tMap<Object, Object> " + var_name + " = new HashMap<>();\n"
                            for key in list(element.keys()):
                                inp_sentence = inp_sentence + "\t\t" + var_name + ".put(" + key + ", " + element[key] + ");\n"
                            element = var_name
                        param_value_java = param_value_java + element
                        if elem_idx != len(param_value_python) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Object> " + param_name_python + " = Arrays.asList(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "

                elif param_detail_java[i][1] == "List<Number>":
                    param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        try:
                            if abs(float(convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx]))) >= JAVA_DOUBLE_MAX:
                                might_overflow = True
                        except:
                            pass
                        param_value_java = param_value_java + convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx])
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Number> " + param_name_python + " = Arrays.asList(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "

                elif param_detail_java[i][1] == "double[]":
                    param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        try:
                            if abs(float(convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx]))) >= JAVA_DOUBLE_MAX:
                                might_overflow = True
                        except:
                            pass
                        param_value_java = param_value_java + convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx])
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tdouble[] " + param_name_python + " = {" + param_value_java + "};\n"
                    assert_inps = assert_inps + param_name_python + ", "
                    
                elif param_detail_java[i][1] == "List<Double>":
                    param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        try:
                            if abs(float(convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx]))) >= JAVA_DOUBLE_MAX:
                                might_overflow = True
                        except:
                            pass
                        param_value_java = param_value_java + convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx])
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Double> " + param_name_python + " = List.of(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "
                else:
                    incompatible_error = True
                    java_error_param_type = param_detail_java[i][1]
                    java_error_param_name = param_detail_java[i][0]
                    custom_error_message = f"Python func: {func_name}() accepts {param_type_python}, whereas Java func: {func_name_java}() accepts {java_error_param_type} for variable {java_error_param_name}; using Object type appropriately so that Java function can support multiple types might solve this issue"

            elif param_type_python == "list[int]":
                if param_detail_java[i][1] == "List<Object>":
                    param_value_python = ast.literal_eval(param_value_python)
                    param_value_java = ""
                    for elem_idx in range(len(param_value_python)):
                        element = param_value_python[elem_idx]
                        if type(element) == type(1):
                            try:
                                if abs(float(element)) >= JAVA_INT_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type(1.1):
                            try:
                                if abs(float(element)) >= JAVA_DOUBLE_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type("a"):
                            element = "\"" + element + "\""
                        elif type(element) == type(None):
                            element = "null"
                        elif type(element) == type(True):
                            if element == False:
                                element = str(0)
                            else:
                                element = str(1)
                        elif type(element) == type([]):
                            var_name = "__temp_arr" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tObject[] " + var_name + " = {"
                            for elem_idx2 in range(len(element)):
                                if elem_idx2 != len(element) - 1:
                                    inp_sentence = inp_sentence + element[elem_idx2] + ", "
                                else:
                                    inp_sentence = inp_sentence + element[elem_idx2]
                            inp_sentence = inp_sentence + "};\n"
                            element = var_name
                        elif type(element) == type({}):
                            var_name = "__temp_dict" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tMap<Object, Object> " + var_name + " = new HashMap<>();\n"
                            for key in list(element.keys()):
                                inp_sentence = inp_sentence + "\t\t" + var_name + ".put(" + key + ", " + element[key] + ");\n"
                            element = var_name
                        param_value_java = param_value_java + element
                        if elem_idx != len(param_value_python) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Object> " + param_name_python + " = Arrays.asList(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "

                if param_detail_java[i][1] == "List<Number>":
                    param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        try:
                            if abs(float(convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx]))) >= JAVA_DOUBLE_MAX:
                                might_overflow = True
                        except:
                            pass
                        param_value_java = param_value_java + convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx])
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Number> " + param_name_python + " = Arrays.asList(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "

                if param_detail_java[i][1] == "List<Integer>":
                    param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        try:
                            if all_elements_in_python_list[elem_idx].strip() != "False" and all_elements_in_python_list[elem_idx].strip() != "True" and abs(float(all_elements_in_python_list[elem_idx].strip())) >= JAVA_INT_MAX:
                                might_overflow = True
                        except:
                            pass
                        if all_elements_in_python_list[elem_idx].strip() == "False" or all_elements_in_python_list[elem_idx] == False: param_value_java = param_value_java + "0"
                        elif all_elements_in_python_list[elem_idx].strip() == "True" or all_elements_in_python_list[elem_idx] == True: param_value_java = param_value_java + "1"
                        else: param_value_java = param_value_java + all_elements_in_python_list[elem_idx].strip()
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Integer> " + param_name_python + " = List.of(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "

                if param_detail_java[i][1] == "int[]" or param_detail_java[i][1] == "Integer[]":
                    param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        try:
                            if all_elements_in_python_list[elem_idx].strip() != "False" and all_elements_in_python_list[elem_idx].strip() != "True" and abs(float(all_elements_in_python_list[elem_idx].strip())) >= JAVA_INT_MAX:
                                might_overflow = True
                        except:
                            pass
                        if all_elements_in_python_list[elem_idx].strip() == "False"  or all_elements_in_python_list[elem_idx] == False: param_value_java = param_value_java + "0"
                        elif all_elements_in_python_list[elem_idx].strip() == "True"  or all_elements_in_python_list[elem_idx] == True: param_value_java = param_value_java + "1"
                        else: param_value_java = param_value_java + all_elements_in_python_list[elem_idx].strip()
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\t" + param_detail_java[i][1] + " " + param_name_python + " = {" + param_value_java + "};\n"
                    assert_inps = assert_inps + param_name_python + ", "

                if param_detail_java[i][1] == "List<Double>":
                    param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        try:
                            if abs(float(convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx]))) >= JAVA_DOUBLE_MAX:
                                might_overflow = True
                        except:
                            pass
                        param_value_java = param_value_java + convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx])
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Double> " + param_name_python + " = List.of(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "
                if param_detail_java[i][1] == "Double[]" or param_detail_java[i][1] == "double[]":
                    param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        try:
                            if abs(float(convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx]))) >= JAVA_DOUBLE_MAX:
                                might_overflow = True
                        except:
                            pass
                        param_value_java = param_value_java + convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx])
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\t" + param_detail_java[i][1] + " " + param_name_python + " = {" + param_value_java + "};\n"
                    assert_inps = assert_inps + param_name_python + ", "

            elif param_type_python == "list[str]":
                if param_detail_java[i][1] == "List<Object>":
                    param_value_python = ast.literal_eval(param_value_python)
                    param_value_java = ""
                    for elem_idx in range(len(param_value_python)):
                        element = param_value_python[elem_idx]
                        if type(element) == type(1):
                            try:
                                if abs(float(element)) >= JAVA_INT_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type(1.1):
                            try:
                                if abs(float(element)) >= JAVA_DOUBLE_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type("a"):
                            element = "\"" + element + "\""
                        elif type(element) == type(None):
                            element = "null"
                        elif type(element) == type(True):
                            if element == False:
                                element = str(0)
                            else:
                                element = str(1)
                        elif type(element) == type([]):
                            var_name = "__temp_arr" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tObject[] " + var_name + " = {"
                            for elem_idx2 in range(len(element)):
                                if elem_idx2 != len(element) - 1:
                                    inp_sentence = inp_sentence + element[elem_idx2] + ", "
                                else:
                                    inp_sentence = inp_sentence + element[elem_idx2]
                            inp_sentence = inp_sentence + "};\n"
                            element = var_name
                        elif type(element) == type({}):
                            var_name = "__temp_dict" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tMap<Object, Object> " + var_name + " = new HashMap<>();\n"
                            for key in list(element.keys()):
                                inp_sentence = inp_sentence + "\t\t" + var_name + ".put(" + key + ", " + element[key] + ");\n"
                            element = var_name
                        param_value_java = param_value_java + element
                        if elem_idx != len(param_value_python) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Object> " + param_name_python + " = Arrays.asList(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "
                elif param_detail_java[i][1] == "List<String>":
                    # param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = ast.literal_eval(param_value_python) # param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        param_value_java = param_value_java + "\"" + convert_python_str_to_java_String(all_elements_in_python_list[elem_idx]) + "\""
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<String> " + param_name_python + " = Arrays.asList(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "
                elif param_detail_java[i][1] == "String[]":
                    # param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = ast.literal_eval(param_value_python) # param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        param_value_java = param_value_java + "\"" + convert_python_str_to_java_String(all_elements_in_python_list[elem_idx]) + "\""
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tString[] " + param_name_python + " = new String[]{" + param_value_java + "};\n"
                    assert_inps = assert_inps + param_name_python + ", "
                elif param_detail_java[i][1] == "char[]":
                    # param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = ast.literal_eval(param_value_python) # param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        param_value_java = param_value_java + "'" + convert_python_str_to_java_Char_Array(all_elements_in_python_list[elem_idx]) + "'"
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tchar[] " + param_name_python + " = {" + param_value_java + "};\n"
                    assert_inps = assert_inps + param_name_python + ", "
                else:
                    incompatible_error = True
                    java_error_param_type = param_detail_java[i][1]
                    java_error_param_name = param_detail_java[i][0]
                    custom_error_message = f"Python func: {func_name}() accepts {param_type_python}, whereas Java func: {func_name_java}() accepts {java_error_param_type} for variable {java_error_param_name}; using Object type appropriately so that Java function can support multiple types might solve this issue"
                
            elif param_type_python == "list[object]":
                if param_detail_java[i][1] == "List<Object>":
                    incompatible_error = False
                    param_value_python = ast.literal_eval(param_value_python)
                    param_value_java = ""
                    for elem_idx in range(len(param_value_python)):
                        element = param_value_python[elem_idx]
                        if type(element) == type(1):
                            try:
                                if abs(float(element)) >= JAVA_INT_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type(1.1):
                            try:
                                if abs(float(element)) >= JAVA_DOUBLE_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type("a"):
                            element = "\"" + element + "\""
                        elif type(element) == type(None):
                            element = "null"
                        elif type(element) == type(True):
                            if element == False:
                                element = str(0)
                            else:
                                element = str(1)
                        elif type(element) == type([]):
                            var_name = "__temp_arr" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tObject[] " + var_name + " = {"
                            for elem_idx2 in range(len(element)):
                                if elem_idx2 != len(element) - 1:
                                    inp_sentence = inp_sentence + element[elem_idx2] + ", "
                                else:
                                    inp_sentence = inp_sentence + element[elem_idx2]
                            inp_sentence = inp_sentence + "};\n"
                            element = var_name
                        elif type(element) == type({}):
                            var_name = "__temp_dict" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tMap<Object, Object> " + var_name + " = new HashMap<>();\n"
                            for key in list(element.keys()):
                                inp_sentence = inp_sentence + "\t\t" + var_name + ".put(" + key + ", " + element[key] + ");\n"
                            element = var_name
                        param_value_java = param_value_java + element
                        if elem_idx != len(param_value_python) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Object> " + param_name_python + " = Arrays.asList(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "
                else:
                    # should compose this test in a way that raises error with the message
                    # Python accepts Object, Java only accepts {param_detail_java[i][1]}
                    incompatible_error = True
                    java_error_param_type = param_detail_java[i][1]
                    java_error_param_name = param_detail_java[i][0]
                    custom_error_message = f"Python func: {func_name}() accepts {param_type_python}, whereas Java func: {func_name_java}() accepts {java_error_param_type} for variable {java_error_param_name}; using Object type appropriately so that Java function can support multiple types might solve this issue"

            elif param_type_python == "list[list]":
                if param_detail_java[i][1] == "int[][]":
                    param_value_python = ast.literal_eval(param_value_python)
                    param_value_java = ""
                    for row in param_value_python:
                        param_value_java = param_value_java + "{"
                        extra_added = False
                        for element in row:
                            try:
                                if abs(float(element)) >= JAVA_INT_MAX:
                                    might_overflow = True
                            except:
                                pass
                            extra_added = True
                            param_value_java = param_value_java + str(element) + ", "
                        if extra_added: param_value_java = param_value_java[:-2] + "}, "
                        else: param_value_java = param_value_java + "}, "

                    param_value_java = param_value_java[:-2]
                    inp_sentence = inp_sentence + "\t\tint[][] " + param_name_python + " = {" + param_value_java + "};\n"
                    assert_inps = assert_inps + param_name_python + ", "
                    
                if param_detail_java[i][1] == "List<List<Integer>>":
                    param_value_python = ast.literal_eval(param_value_python)
                    param_value_java = ""
                    for row in param_value_python:
                        param_value_java = param_value_java + "List.of("
                        extra_added = False
                        for element in row:
                            try:
                                if element != "False" and element != "True" and abs(float(element)) >= JAVA_INT_MAX:
                                    might_overflow = True
                            except:
                                pass
                            if element == "False" or element == False: param_value_java = param_value_java + "0, "
                            elif element == "True" or element == True: param_value_java = param_value_java + "1, "
                            else: param_value_java = param_value_java = param_value_java + str(element) + ", "
                            extra_added = True
                        if extra_added: param_value_java = param_value_java[:-2] + "), "
                        else: param_value_java = param_value_java + "), "

                    param_value_java = param_value_java[:-2]
                    inp_sentence = inp_sentence + "\t\tList<List<Integer>> " + param_name_python + " = List.of(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "

            elif param_type_python == "list":
                if param_detail_java[i][1] == "int[]" or param_detail_java[i][1] == "Integer[]":
                    param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        try:
                            if all_elements_in_python_list[elem_idx].strip() != "False" and all_elements_in_python_list[elem_idx].strip() != "True" and abs(float(all_elements_in_python_list[elem_idx].strip())) >= JAVA_INT_MAX:
                                might_overflow = True
                        except:
                            pass
                        if all_elements_in_python_list[elem_idx].strip() == "False" or all_elements_in_python_list[elem_idx] == False: param_value_java = param_value_java + "0"
                        elif all_elements_in_python_list[elem_idx].strip() == "True" or all_elements_in_python_list[elem_idx] == True: param_value_java = param_value_java + "1"
                        else: param_value_java = param_value_java + all_elements_in_python_list[elem_idx].strip()
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\t" + param_detail_java[i][1] + " " + param_name_python + " = {" + param_value_java + "};\n"
                    assert_inps = assert_inps + param_name_python + ", "
                if param_detail_java[i][1] == "List<Integer>":
                    param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        try:
                            if all_elements_in_python_list[elem_idx].strip() != "False" and all_elements_in_python_list[elem_idx].strip() != "True" and abs(float(all_elements_in_python_list[elem_idx].strip())) >= JAVA_INT_MAX:
                                might_overflow = True
                        except:
                            pass
                        if all_elements_in_python_list[elem_idx].strip() == "False"  or all_elements_in_python_list[elem_idx] == False: param_value_java = param_value_java + "0"
                        elif all_elements_in_python_list[elem_idx].strip() == "True"  or all_elements_in_python_list[elem_idx] == True: param_value_java = param_value_java + "1"
                        else: param_value_java = param_value_java + all_elements_in_python_list[elem_idx].strip()
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Integer> " + param_name_python + " = List.of(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "

                if param_detail_java[i][1] == "List<String>":
                    # param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = ast.literal_eval(param_value_python) # param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        param_value_java = param_value_java + "\"" + convert_python_str_to_java_String(all_elements_in_python_list[elem_idx]) + "\""
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<String> " + param_name_python + " = Arrays.asList(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "
                
                if param_detail_java[i][1] == "String[]":
                    # param_value_python = param_value_python[1:(len(param_value_python) - 1)]
                    all_elements_in_python_list = ast.literal_eval(param_value_python) # param_value_python.strip().split(",")
                    param_value_java = ""
                    for elem_idx in range(len(all_elements_in_python_list)):
                        param_value_java = param_value_java + "\"" + convert_python_str_to_java_String(all_elements_in_python_list[elem_idx]) + "\""
                        if elem_idx != len(all_elements_in_python_list) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tString[] " + param_name_python + " = new String[]{" + param_value_java + "};\n"
                    assert_inps = assert_inps + param_name_python + ", "

                if param_detail_java[i][1] == "List<Object>":
                    param_value_python = ast.literal_eval(param_value_python)
                    param_value_java = ""
                    for elem_idx in range(len(param_value_python)):
                        element = param_value_python[elem_idx]
                        if type(element) == type(1):
                            try:
                                if abs(float(element)) >= JAVA_INT_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type(1.1):
                            try:
                                if abs(float(element)) >= JAVA_DOUBLE_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type("a"):
                            element = "\"" + element + "\""
                        elif type(element) == type(None):
                            element = "null"
                        elif type(element) == type(True):
                            if element == False:
                                element = str(0)
                            else:
                                element = str(1)
                        elif type(element) == type([]):
                            var_name = "__temp_arr" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tObject[] " + var_name + " = {"
                            for elem_idx2 in range(len(element)):
                                if elem_idx2 != len(element) - 1:
                                    inp_sentence = inp_sentence + element[elem_idx2] + ", "
                                else:
                                    inp_sentence = inp_sentence + element[elem_idx2]
                            inp_sentence = inp_sentence + "};\n"
                            element = var_name
                        elif type(element) == type({}):
                            var_name = "__temp_dict" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tMap<Object, Object> " + var_name + " = new HashMap<>();\n"
                            for key in list(element.keys()):
                                inp_sentence = inp_sentence + "\t\t" + var_name + ".put(" + key + ", " + element[key] + ");\n"
                            element = var_name
                        param_value_java = param_value_java + element
                        if elem_idx != len(param_value_python) - 1:
                            param_value_java = param_value_java + ", "
                    inp_sentence = inp_sentence + "\t\tList<Object> " + param_name_python + " = Arrays.asList(" + param_value_java + ");\n"
                    assert_inps = assert_inps + param_name_python + ", "

            elif param_type_python == "dict":
                if param_detail_java[i][1] == "Map<Object, Object>":
                    param_value_python = ast.literal_eval(param_value_python)
                    keys = list(param_value_python.keys())
                    
                    put_sentence = ""
                    for key in keys:
                        val = param_value_python[key]
                        key_type = type(key)
                        val_type = type(val)
                        put_sentence = put_sentence + "\t\tdict.put(__key_type__, __val_type__);\n"
                        if key_type == type(""):
                            put_sentence = put_sentence.replace("__key_type__", f"\"{convert_python_str_to_java_String(key)}\"")
                        else:
                            put_sentence = put_sentence.replace("__key_type__", f"{key}")
                        
                        if val_type == type(""):
                            put_sentence = put_sentence.replace("__val_type__", f"\"{convert_python_str_to_java_String(val)}\"")
                        else:
                            put_sentence = put_sentence.replace("__val_type__", f"{val}")
                        
                    inp_sentence = inp_sentence + "\t\tMap<Object, Object> " + param_name_python + "= new HashMap<>();\n"
                    inp_sentence = inp_sentence + put_sentence

                    assert_inps = assert_inps + param_name_python + ", "
                
            elif param_type_python == "tuple":
                if param_detail_java[i][1] == "int[]":
                    param_value_python = ast.literal_eval(param_value_python)
                    inp_sentence = inp_sentence + "\t\tint[] " + param_name_python + " = {" + str(param_value_python[0]) + ", " + str(param_value_python[1]) + "};\n"

                    assert_inps = assert_inps + param_name_python + ", "
                

        else:
            python_ret_type = params[i][1]
            expected_output_java = ""
            if java_ret_type == "float":
                expected_output_java = f"{func_output}F"
                try:
                    if abs(float(func_output)) >= JAVA_FLOAT_MAX:
                        might_overflow = True
                except:
                    pass
                out_sentence = out_sentence + "\t\tfloat expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "double":
                expected_output_java = f"{func_output}"
                try:
                    if abs(float(func_output)) >= JAVA_DOUBLE_MAX:
                        might_overflow = True
                except:
                    pass
                out_sentence = out_sentence + "\t\tdouble expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "int":
                expected_output_java = f"{func_output}"
                try:
                    if func_output != "False" and func_output != "True" and abs(float(func_output)) >= JAVA_INT_MAX:
                        might_overflow = True
                except:
                    pass
                if func_output == "False"  or func_output == False: expected_output_java = "0"
                if func_output == "True"  or func_output == True: expected_output_java = "1"
                out_sentence = out_sentence + "\t\tint expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "Integer":
                expected_output_java = f"{func_output}"
                try:
                    if func_output != "False" and func_output != "True" and abs(float(func_output)) >= JAVA_INT_MAX:
                        might_overflow = True
                except:
                    pass
                if func_output == "False" or func_output == False: expected_output_java = "0"
                if func_output == "True" or func_output == True: expected_output_java = "1"
                out_sentence = out_sentence + "\t\tInteger expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "BigInteger":
                expected_output_java = f"new BigInteger(\"{func_output}\")"
                out_sentence = out_sentence + "\t\tBigInteger expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "Number":
                func_output = ast.literal_eval(func_output)
                try:
                    if func_output != "False" and func_output != "True" and abs(float(func_output)) >= JAVA_DOUBLE_MAX:
                        might_overflow = True
                except:
                    pass
                if type(func_output) == type(0.1):
                    expected_output_java = f"new Double({str(func_output)})"
                elif type(func_output) == type(1):
                    expected_output_java = f"new Double({str(func_output)}.0)"
                if func_output == "False" or func_output == False: expected_output_java = "0"
                if func_output == "True" or func_output == True: expected_output_java = "1"
                out_sentence = out_sentence + "\t\tNumber expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "long":
                expected_output_java = f"{func_output}L"
                try:
                    if abs(float(func_output)) >= JAVA_LONG_MAX:
                        might_overflow = True
                except:
                    pass
                out_sentence = out_sentence + "\t\tlong expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "boolean":
                expected_output_java = f"{func_output.lower()}"
                out_sentence = out_sentence + "\t\tboolean expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "String":
                expected_output_java = f"{func_output}"
                out_sentence = out_sentence + "\t\tString expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "char":
                expected_output_java = func_output.replace("\"", "")
                expected_output_java = f"'{expected_output_java}'"
                out_sentence = out_sentence + "\t\tchar expected = " + "====XXXX====" + ";\n"
            elif java_ret_type.startswith("Optional<String>"):
                expected_output_java = "Optional.of("
                expected_output_java = expected_output_java + convert_python_str_to_java_String(func_output)
                expected_output_java = expected_output_java + ")"
                out_sentence = out_sentence + f"\t\t{java_ret_type} expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "List<String>":
                # param_value_python = func_output[1:(len(func_output) - 1)]
                all_elements_in_python_list = ast.literal_eval(func_output) # param_value_python.strip().split(",")
                expected_output_java = "Arrays.asList("
                for elem_idx in range(len(all_elements_in_python_list)):
                    expected_output_java = expected_output_java + "\"" + convert_python_str_to_java_String(all_elements_in_python_list[elem_idx]) + "\""
                    if elem_idx != len(all_elements_in_python_list) - 1:
                        expected_output_java = expected_output_java + ", "
                expected_output_java = expected_output_java + ")"
                out_sentence = out_sentence + "\t\tList<String> expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "String[]":
                # param_value_python = func_output[1:(len(func_output) - 1)]
                all_elements_in_python_list = ast.literal_eval(func_output) # param_value_python.strip().split(",")
                expected_output_java = "new String[]{"
                for elem_idx in range(len(all_elements_in_python_list)):
                    expected_output_java = expected_output_java + "\"" + convert_python_str_to_java_String(all_elements_in_python_list[elem_idx]) + "\""
                    if elem_idx != len(all_elements_in_python_list) - 1:
                        expected_output_java = expected_output_java + ", "
                expected_output_java = expected_output_java + "}"
                out_sentence = out_sentence + "\t\tString[] expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "int[]" or java_ret_type == "Integer[]":
                param_value_python = func_output[1:(len(func_output) - 1)]
                all_elements_in_python_list = param_value_python.strip().split(",")
                expected_output_java = "{"
                for elem_idx in range(len(all_elements_in_python_list)):
                    try:
                        if abs(float(all_elements_in_python_list[elem_idx].strip())) >= JAVA_INT_MAX:
                            might_overflow = True
                    except:
                        pass
                    expected_output_java = expected_output_java + all_elements_in_python_list[elem_idx].strip()
                    if elem_idx != len(all_elements_in_python_list) - 1:
                        expected_output_java = expected_output_java + ", "
                expected_output_java = expected_output_java + "}"
                out_sentence = out_sentence + "\t\t" + java_ret_type + " expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "double[]" or java_ret_type == "Double[]":
                param_value_python = func_output[1:(len(func_output) - 1)]
                all_elements_in_python_list = param_value_python.strip().split(",")
                expected_output_java = "{"
                for elem_idx in range(len(all_elements_in_python_list)):
                    try:
                        if abs(float(all_elements_in_python_list[elem_idx].strip())) >= JAVA_DOUBLE_MAX:
                            might_overflow = True
                    except:
                        pass
                    expected_output_java = expected_output_java + all_elements_in_python_list[elem_idx].strip()
                    if elem_idx != len(all_elements_in_python_list) - 1:
                        expected_output_java = expected_output_java + ", "
                expected_output_java = expected_output_java + "}"
                out_sentence = out_sentence + "\t\t" + java_ret_type + " expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "char[]":
                param_value_python = func_output[1:(len(func_output) - 1)]
                all_elements_in_python_list = param_value_python.strip().split(",")
                expected_output_java = "{"
                for elem_idx in range(len(all_elements_in_python_list)):
                    expected_output_java = expected_output_java + convert_python_str_to_java_Char_Array(all_elements_in_python_list[elem_idx].strip())
                    if elem_idx != len(all_elements_in_python_list) - 1:
                        expected_output_java = expected_output_java + ", "
                expected_output_java = expected_output_java + "}"
                out_sentence = out_sentence + "\t\tchar[] expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "List<Double>":
                param_value_python = func_output[1:(len(func_output) - 1)]
                all_elements_in_python_list = param_value_python.strip().split(",")
                expected_output_java = "List.of("
                for elem_idx in range(len(all_elements_in_python_list)):
                    try:
                        if abs(float(convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx].strip()))) >= JAVA_INT_MAX:
                            might_overflow = True
                    except:
                        pass
                    expected_output_java = expected_output_java + convert_python_int_float_to_java_double(all_elements_in_python_list[elem_idx].strip())
                    if elem_idx != len(all_elements_in_python_list) - 1:
                        expected_output_java = expected_output_java + ", "
                expected_output_java = expected_output_java + ")"
                out_sentence = out_sentence + "\t\tList<Double> expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "List<Integer>":
                param_value_python = func_output[1:(len(func_output) - 1)]
                all_elements_in_python_list = param_value_python.strip().split(",")
                expected_output_java = "List.of("
                for elem_idx in range(len(all_elements_in_python_list)):
                    try:
                        if abs(float(all_elements_in_python_list[elem_idx].strip())) >= JAVA_INT_MAX:
                            might_overflow = True
                        abs(int(all_elements_in_python_list[elem_idx].strip()))
                    except:
                        incompatible_error = True
                        java_error_param_type = java_ret_type
                        custom_error_message = f"Python func: {func_name}() returns {python_ret_type}, whereas Java func: {func_name_java}() returns {java_error_param_type}; using Object type appropriately so that Java function can support multiple types might solve this issue"
                    expected_output_java = expected_output_java + all_elements_in_python_list[elem_idx].strip()
                    if elem_idx != len(all_elements_in_python_list) - 1:
                        expected_output_java = expected_output_java + ", "
                expected_output_java = expected_output_java + ")"
                out_sentence = out_sentence + "\t\tList<Integer> expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "List<int[]>":
                if params[i][1] == "list[tuple]":
                    func_output = ast.literal_eval(func_output)
                    expected_output_java = "List.of("
                    extra_added = False
                    for elem_idx in range(len(func_output)):
                        extra_added = True
                        item1, item2 = func_output[elem_idx]
                        if item1 == None and item2 == None: expected_output_java = expected_output_java + "new int[]{}" + ", "
                        else:
                            try:
                                if abs(float(item1)) >= JAVA_INT_MAX or abs(float(item2)) >= JAVA_INT_MAX:
                                    might_overflow = True
                                abs(int(item1))
                                abs(int(item2))
                            except:
                                incompatible_error = True
                                java_error_param_type = java_ret_type
                                custom_error_message = f"Python func: {func_name}() returns {python_ret_type}, whereas Java func: {func_name_java}() returns {java_error_param_type}; using Object type appropriately so that Java function can support multiple types might solve this issue"
                            expected_output_java = expected_output_java + "new int[]{" + str(item1) + ", " + str(item2) + "}, "
                    if extra_added: expected_output_java = expected_output_java[:-2] + ")"
                    else: expected_output_java = expected_output_java + ")"
                    out_sentence = out_sentence + "\t\tList<int[]> expected = " + "====XXXX====" + ";\n"

            elif java_ret_type == "Object":
                if f"{func_output}".startswith("[") and f"{func_output}".endswith("]"):
                    func_output = ast.literal_eval(func_output)
                    expected_output_java = "Arrays.asList("
                    for elem_idx in range(len(func_output)):
                        if type(func_output[elem_idx]) == type(""):
                            expected_output_java = expected_output_java + "\"" + convert_python_str_to_java_String(func_output[elem_idx]) + "\""
                            if elem_idx != len(func_output) - 1:
                                expected_output_java = expected_output_java + ", "
                    expected_output_java = expected_output_java + ")"
                        
                elif f"{func_output}".startswith("{") and f"{func_output}".endswith("}"):
                    pass
                elif f"{func_output}".startswith("\"") and f"{func_output}".endswith("\""):
                    expected_output_java = f"new String({func_output})"
                elif "." in f"{func_output}":
                    try:
                        if abs(float(func_output)) >= JAVA_DOUBLE_MAX:
                            might_overflow = True
                    except:
                        pass
                    expected_output_java = f"new Double({func_output})"
                else:
                    try:
                        if abs(float(func_output)) >= JAVA_INT_MAX:
                            might_overflow = True
                    except:
                        pass
                    expected_output_java = f"new Integer({func_output})"

                out_sentence = out_sentence + "\t\tObject expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "Object[]":
                if (f"{func_output}".startswith("[") and f"{func_output}".endswith("]")) or (f"{func_output}".startswith("(") and f"{func_output}".endswith(")")):
                    func_output = ast.literal_eval(func_output)
                    expected_output_java = "new Object[]{"
                    for elem_idx in range(len(func_output)):
                        element = func_output[elem_idx]
                        if type(element) == type(1):
                            try:
                                if abs(float(element)) >= JAVA_INT_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type(1.1):
                            try:
                                if abs(float(element)) >= JAVA_DOUBLE_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type("a"):
                            element = "\"" + element + "\""
                        elif type(element) == type(None):
                            element = "null"
                        elif type(element) == type(True):
                            if element == False:
                                element = str(0)
                            else:
                                element = str(1)
                        elif type(element) == type([]):
                            var_name = "__temp_arr" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tObject[] " + var_name + " = {"
                            for elem_idx2 in range(len(element)):
                                if elem_idx2 != len(element) - 1:
                                    inp_sentence = inp_sentence + element[elem_idx2] + ", "
                                else:
                                    inp_sentence = inp_sentence + element[elem_idx2]
                            inp_sentence = inp_sentence + "};\n"
                            element = var_name
                        elif type(element) == type({}):
                            var_name = "__temp_dict" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tMap<Object, Object> " + var_name + " = new HashMap<>();\n"
                            for key in list(element.keys()):
                                inp_sentence = inp_sentence + "\t\t" + var_name + ".put(" + key + ", " + element[key] + ");\n"
                            element = var_name
                        expected_output_java = expected_output_java + element
                        if elem_idx != len(func_output) - 1:
                            expected_output_java = expected_output_java + ", "
                    expected_output_java = expected_output_java + "}"
                out_sentence = out_sentence + "\t\tObject[] expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "List<Object>":
                if (f"{func_output}".startswith("[") and f"{func_output}".endswith("]")) or (f"{func_output}".startswith("(") and f"{func_output}".endswith(")")):
                    func_output = ast.literal_eval(func_output)
                    expected_output_java = "Arrays.asList("
                    for elem_idx in range(len(func_output)):
                        element = func_output[elem_idx]
                        if type(element) == type(1):
                            try:
                                if abs(float(element)) >= JAVA_INT_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type(1.1):
                            try:
                                if abs(float(element)) >= JAVA_DOUBLE_MAX:
                                    might_overflow = True
                            except:
                                pass
                            element = str(element)
                        elif type(element) == type("a"):
                            element = "\"" + element + "\""
                        elif type(element) == type(None):
                            element = "null"
                        elif type(element) == type(True):
                            if element == False:
                                element = str(0)
                            else:
                                element = str(1)
                        elif type(element) == type([]):
                            var_name = "__temp_arr" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tObject[] " + var_name + " = {"
                            for elem_idx2 in range(len(element)):
                                if elem_idx2 != len(element) - 1:
                                    inp_sentence = inp_sentence + element[elem_idx2] + ", "
                                else:
                                    inp_sentence = inp_sentence + element[elem_idx2]
                            inp_sentence = inp_sentence + "};\n"
                            element = var_name
                        elif type(element) == type({}):
                            var_name = "__temp_dict" + str(i) + "__"
                            inp_sentence = inp_sentence + "\t\tMap<Object, Object> " + var_name + " = new HashMap<>();\n"
                            for key in list(element.keys()):
                                inp_sentence = inp_sentence + "\t\t" + var_name + ".put(" + key + ", " + element[key] + ");\n"
                            element = var_name
                        expected_output_java = expected_output_java + element
                        if elem_idx != len(func_output) - 1:
                            expected_output_java = expected_output_java + ", "
                    expected_output_java = expected_output_java + ")"
                out_sentence = out_sentence + "\t\tList<Object> expected = " + "====XXXX====" + ";\n"
            elif java_ret_type == "Map<String, Integer>":
                func_output = ast.literal_eval(func_output)
                keys = list(func_output.keys())
                out_sentence = out_sentence + "\t\t" + java_ret_type + " expected = new HashMap<>();\n"
                for key in keys:
                    val = func_output[key]
                    key_type = type(key)
                    val_type = type(val)
                    out_sentence = out_sentence + "\t\texpected.put(__key_type__, __val_type__);\n"
                    if key_type == type(""):
                        out_sentence = out_sentence.replace("__key_type__", f"\"{convert_python_str_to_java_String(key)}\"")
                    elif key_type == type(1):
                        try:
                            if abs(float(key)) >= JAVA_INT_MAX:
                                might_overflow = True
                        except:
                            pass
                        out_sentence = out_sentence.replace("__key_type__", f"{key}")
                            
                    if val_type == type(""):
                        out_sentence = out_sentence.replace("__val_type__", f"\"{convert_python_str_to_java_String(val)}\"")
                    elif val_type == type(1):
                        try:
                            if abs(float(val)) >= JAVA_INT_MAX:
                                might_overflow = True
                        except:
                            pass
                        out_sentence = out_sentence.replace("__val_type__", f"{val}")
            elif java_ret_type == "Tuple<Integer, Integer>" or java_ret_type == "Tuple":
                func_output = ast.literal_eval(func_output)
                items = []
                for i in range(len(func_output)):
                    if type(func_output[i]) == type(None):
                        items.append("null")
                    else:
                        items.append(func_output[i])
                        
                out_sentence = out_sentence + "\t\t" + java_ret_type + " expected = new Tuple<>(" + str(items[0]) + ", " + str(items[1]) + ");\n"

            if func_output == "NoneType" or func_output == "None" or func_output == None: expected_output_java = "null"
            out_sentence = out_sentence.replace("====XXXX====", expected_output_java)

    assert_inps = assert_inps[:-2]
    if incompatible_error:
        normalized_func_input = convert_python_str_to_java_String(utility.shorten_middle(func_input)).replace("\"", "\\\"")
        normalized_func_output = convert_python_str_to_java_String(utility.shorten_middle(func_output)).replace("\"", "\\\"")
        test_str = test_str + "\t\t" + f"fail(\"Incompatible Python Test: {test_name}:self.assertEqual({normalized_func_output}, {func_name}({normalized_func_input})); {custom_error_message}\");" + "\n\t}"
    elif might_overflow:
        normalized_func_input = convert_python_str_to_java_String(utility.shorten_middle(func_input)).replace("\"", "\\\"")
        normalized_func_output = convert_python_str_to_java_String(utility.shorten_middle(func_output)).replace("\"", "\\\"")
        test_str = test_str + "\t\t" + f"fail(\"Java Variable Overflow Issue for Python Test: {test_name}:self.assertEqual({normalized_func_output}, {func_name}({normalized_func_input})); using bigger data types in Java might help\");" + "\n\t}"
    else:
        if java_ret_type == "float" or java_ret_type == "double":
            test_str = test_str + inp_sentence + out_sentence + "\t\tassertEquals(expected, " + code_id + "." + func_name_java + "(" + assert_inps + "), 0.00001" + ");" + "\n\t}"
        elif java_ret_type == "int[]" or java_ret_type == "char[]":
            test_str = test_str + inp_sentence + out_sentence + "\t\tassertArrayEquals(expected, " + code_id + "." + func_name_java + "(" + assert_inps + ")" + ");" + "\n\t}"
        elif java_ret_type == "double[]":
            test_str = test_str + inp_sentence + out_sentence + "\t\tassertArrayEquals(expected, " + code_id + "." + func_name_java + "(" + assert_inps + "), 0.00001" + ");" + "\n\t}"
        elif java_ret_type == "Tuple<Integer, Integer>" or java_ret_type == "Tuple":
            test_str = test_str + inp_sentence + out_sentence + "\t\tassertEquals(expected.x, " + code_id + "." + func_name_java + "(" + assert_inps + ").x);\n" + "\t\tassertEquals(expected.y, " + code_id + "." + func_name_java + "(" + assert_inps + ").y" + ");" + "\n\t}"
        else:
            test_str = test_str + inp_sentence + out_sentence + "\t\tassertEquals(expected, " + code_id + "." + func_name_java + "(" + assert_inps + ")" + ");" + "\n\t}"
    
    if len(test_str) < 2000:
        return test_str

    return ""

def convert(translated_file, test_info):
    code_id = Path(translated_file).stem
    if code_id == "__pycache__" or code_id == "__init__" or code_id.endswith("temp"):
        return

    if Path(translated_file).name.endswith(".class"):
        return
            
    params = test_info["params"]
    try:
        total_extracted = test_info["total_extracted"]
    except KeyError as e:
        print(e, "for file", code_id)

    java_test_funcs = []

    for i in range(total_extracted):
        sample_test_info = test_info["tests"][i]
        test_name = sample_test_info["test_name"]
        func_name = sample_test_info["test_func"]
        func_input = sample_test_info["func_input"]
        func_output = sample_test_info["expected_output"]
        java_code_snippet = ""
        try:
            java_code_snippet = convert_to_java(func_name, func_input, func_output, test_name, params, translated_file, code_id)
            java_test_funcs.append(java_code_snippet)
        except Exception as e:
            pass

    java_file_content = "import org.junit.Test;\nimport static org.junit.Assert.*;\nimport java.util.*;\nimport java.math.*;\n\npublic class " + code_id + "Test" + "{"
    for i in range(total_extracted):
        try:
            java_file_content = java_file_content + "\n" + java_test_funcs[i] + "\n"
        except:
            pass

    java_file_content = java_file_content + "}"

    return java_file_content


def infer_param_types_and_extract_test_info(source_file, test_file, root_dir, temp_dir):
    file_test_results = {}
    test_content = load_source_content(test_file)
    infer_type_file_content = load_source_content(f"{root_dir}/determine_parameter_type.py")
    source_file_content = load_source_content(source_file)
    new_file_content = infer_type_file_content + "\n\n" + source_file_content
    extraction_res, extraction_details = get_test_details(get_single_test(test_content, "test_1"))
    code_id = Path(source_file).stem
    current_test_file = f"{temp_dir}/infer_type_{code_id}.py"
    params = ""
    if extraction_res:
        func_name = extraction_details["test_func"]
        func_input = extraction_details["func_input"]
        new_file_content = new_file_content + "\n\n" + "dir = \"" + temp_dir + "/infered_type_" + code_id + ".txt\"\n" + "with open(dir, \"w\") as __f__:\n"
        new_file_content = new_file_content + "\n    inferred_types = infer_types_at_runtime(" + func_name + "," + func_input + ")\n    " + "for i in range(len(inferred_types)):\n        print(f\"{inferred_types[i][0]}: {inferred_types[i][1]}\", file=__f__)"
        new_file_content = new_file_content + "\n    ret_type = infer_return_type(" + func_name + "," + func_input + ")\n    print(f\"return: {ret_type}\", file=__f__)\n"
        new_file_content = new_file_content + "    __f__.close()\n"

        with open(current_test_file, "w") as f:
            print(new_file_content, file=f)
        f.close()

        run_files_to_generate_testfiles(current_test_file)

        if wait_for_file(f"{temp_dir}/infered_type_{code_id}.txt", timeout=100):
            params = load_source_content_arr(f"{temp_dir}/infered_type_{code_id}.txt")
        
    params = [[param.strip().split(":", 1)[0].strip(), param.strip().split(":", 1)[1].strip()] for param in params]

    test_content_arr = load_source_content_arr(test_file)

    no_of_tests = len(test_content_arr)
    passed_extraction = 0
    formatted_tests = []
    for i in range(len(test_content_arr)):
        single_test = test_content_arr[i].strip()
        extraction_res, extraction_details = get_test_details(single_test)
        if extraction_res:
            passed_extraction = passed_extraction + 1
            formatted_tests.append(extraction_details)

    if passed_extraction == no_of_tests:
        file_test_results["params"] = params
        file_test_results["all_extracted"] = 1
        file_test_results["total_extracted"] = no_of_tests
        file_test_results["tests"] = formatted_tests
    
    return file_test_results
    

