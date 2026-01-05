import re
import time, os
import Constants

def extract_code_snippets(text):
    """
    Extracts all code snippets enclosed in triple backticks from the text.
    If no such blocks exist, treats the whole text as a single code snippet.
    """
    code_blocks = re.findall(r'```(?:[\w+]*\n)?(.*?)```', text, re.DOTALL)
    code_blocks = [block.strip() for block in code_blocks]

    if not code_blocks:
        # If no backticks, treat the entire text as a code snippet if it looks like code
        if looks_like_code(text):
            code_blocks.append(text.strip())
        else:
            code_blocks.append("")

    return code_blocks

def looks_like_code(text):
    """
    A simple heuristic to decide if a text looks like code:
    - Contains multiple lines
    - Has typical code patterns (like 'def', 'class', '=', 'import', 'return', braces, etc.)
    """
    code_keywords = ['def ', 'class ', 'import ', 'return', 'if ', 'else', '=', 'for ', 'while ', '(', ')', '{', '}', ':']
    lines = text.strip().splitlines()
    if len(lines) < 2:
        return False
    score = sum(any(kw in line for kw in code_keywords) for line in lines)
    return score / len(lines) > 0.3  # at least 30% of lines should look like code

def get_longest_code_snippet(text):
    """
    Returns the longest code snippet from the text.
    """
    code_snippets = extract_code_snippets(text)
    if not code_snippets:
        return None
    return max(code_snippets, key=len)

def remove_Tuple_class(code_snippet):
    index = code_snippet.find("class Tuple")
    if index != -1:

        prev_part = code_snippet[:index]

        last_curly_end = prev_part.rfind("}")
        prev_part = code_snippet[:last_curly_end + 1]
        last_part = code_snippet[index:]
        no_of_curly = 1
        opening_curly = last_part.find("{")
        last_part = last_part[opening_curly:]

        tuple_end_at = -1

        for i in range(1, len(last_part), 1):
            if last_part[i] == "{":
                no_of_curly += 1
            elif last_part[i] == "}":
                no_of_curly -= 1

            if no_of_curly == 0:
                tuple_end_at = i
                break

        if tuple_end_at != -1:
            last_part = last_part[tuple_end_at + 1:]

        return prev_part + "\n" + last_part, True
    else:
        return code_snippet, False


def wait_for_file(filepath, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(filepath):
            return True
        time.sleep(0.1)
    return False


def classify_junit_output_simple(output: str) -> str:
    if "java.lang.AssertionError" in output:
        return Constants.TEST_MISMATCH
    return Constants.RUNTIME_ERROR