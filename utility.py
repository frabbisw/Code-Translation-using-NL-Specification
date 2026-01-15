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

def remove_class(code_snippet, class_name):
    index = code_snippet.find(class_name)
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


def remove_Tuple_class(code_snippet, main_class_name):
    matches = list(re.finditer(r'\bclass\s+(\w+)', code_snippet))

    new_code = code_snippet
    removed = False

    for m in matches:
        class_name = m.group(1)

        # skip main class
        if class_name != main_class_name:
            new_code, removed = remove_class(new_code, f"class {class_name}")
            cn = re.escape(class_name)
            new_code = re.sub(rf'\b{cn}\s*<', 'Tuple<', new_code)
            new_code = re.sub(rf'\bnew\s+{cn}\b', 'new Tuple', new_code)
            new_code = re.sub(rf'\b{cn}\b', 'Tuple', new_code)
        
    return new_code, removed


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


def extract_failed_junit_tests(junit_output):
    pattern = re.compile(r"\d+\)\s+([a-zA-Z_][a-zA-Z0-9_]*)\(")
    return pattern.findall(junit_output)

def get_single_test(tests_str: str, test_name: str):
    for line in tests_str.splitlines():
        line = line.strip()
        if line.startswith(f"{test_name}:"):
            return line
    return None

def load_source_content(source_file):
    content = None
    with open(source_file, "r") as f:
        content = f.read()
        f.close()
    return content

def normalize_java_util(response: str) -> str:
    # 1) Add "import java.util.*;" if missing (put it after package line if any)
    if not re.search(r'^\s*import\s+java\.util\.\*;\s*$', response, flags=re.MULTILINE):
        if re.search(r'^\s*package\s+[\w.]+;\s*$', response, flags=re.MULTILINE):
            response = re.sub(
                r'^(\s*package\s+[\w.]+;\s*)$',
                r'\1\nimport java.util.*;',
                response,
                flags=re.MULTILINE
            )
        else:
            response = "import java.util.*;\n" + response

    # 2) De-qualify common java.util types (add more if you see them)
    util_types = [
        "Map", "Set", "List", "ArrayList", "HashMap", "HashSet",
        "LinkedHashMap", "LinkedHashSet", "TreeMap", "TreeSet",
        "Deque", "ArrayDeque", "Queue", "PriorityQueue",
        "Collections", "Arrays", "Optional"
    ]
    pattern = r'\bjava\.util\.(?:' + "|".join(map(re.escape, util_types)) + r')\b'
    response = re.sub(pattern, lambda m: m.group(0).split(".")[-1], response)

    return response


def shorten_middle(s: str, keep: int = 250) -> str:
    if len(s) <= 2 * keep:
        return s
    return s[:keep] + "..." + s[-keep:]