import inspect

def infer_return_type(func, *args):
    result = func(*args)
    if isinstance(result, list):
        unique_types = {type(element).__name__ for element in result}
        return f'list[{", ".join(unique_types)}]'
    elif isinstance(result, tuple):
        unique_types = {type(element).__name__ for element in result}
        return f'tuple({", ".join(unique_types)})'
    else:
        return type(result).__name__

def get_function_parameters(func):
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    return params

def infer_types_at_runtime(func, *args):
    param_names = get_function_parameters(func)
    param_types = []

    for name, arg in zip(param_names, args):
        if isinstance(arg, list):
            unique_types = {type(element).__name__ for element in arg}
            param_types.append([name, f'list[{", ".join(unique_types)}]'])
        else:
            param_types.append([name, type(arg).__name__])
    return param_types

from typing import List, Tuple


def find_closest_elements(numbers: List[float]) -> Tuple[float, float]:
    """ From a supplied list of numbers (of length at least two) select and return two that are the closest to each
    other and return them in order (smaller number, larger number).
    >>> find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.2])
    (2.0, 2.2)
    >>> find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.0])
    (2.0, 2.0)
    """

    numbers.sort()
    min_diff = float("inf")
    min_pair = None
    for l, r in zip(numbers[:-1], numbers[1:]):
        diff = r - l
        if diff < min_diff:
            min_diff = diff
            min_pair = (l, r)
    return min_pair



dir = "/home/soumit/Thesis/NL-specification-driven-Code-Translation/Code-Translation-using-NL-Specification/debug_temp_evalplus_test/infered_type_HumanEval_20.txt"
with open(dir, "w") as __f__:

    inferred_types = infer_types_at_runtime(find_closest_elements,[1.0, 2.0, 5.9, 4.0, 5.0])
    for i in range(len(inferred_types)):
        print(f"{inferred_types[i][0]}: {inferred_types[i][1]}", file=__f__)
    ret_type = infer_return_type(find_closest_elements,[1.0, 2.0, 5.9, 4.0, 5.0])
    print(f"return: {ret_type}", file=__f__)
    __f__.close()

