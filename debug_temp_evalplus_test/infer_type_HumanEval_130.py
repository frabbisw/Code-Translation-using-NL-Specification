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

def tri(n):
    """Everyone knows Fibonacci sequence, it was studied deeply by mathematicians in 
    the last couple centuries. However, what people don't know is Tribonacci sequence.
    Tribonacci sequence is defined by the recurrence:
    tri(1) = 3
    tri(n) = 1 + n / 2, if n is even.
    tri(n) =  tri(n - 1) + tri(n - 2) + tri(n + 1), if n is odd.
    For example:
    tri(2) = 1 + (2 / 2) = 2
    tri(4) = 3
    tri(3) = tri(2) + tri(1) + tri(4)
           = 2 + 3 + 3 = 8 
    You are given a non-negative integer number n, you have to a return a list of the 
    first n + 1 numbers of the Tribonacci sequence.
    Examples:
    tri(3) = [1, 3, 2, 8]
    """

    if n == 0: return [1]
    if n == 1: return [1, 3]
    ans = [1, 3]
    for i in range(2, n + 1):
        if i % 2 == 0:
            ans.append(1 + i / 2)
        else:
            ans.append(ans[-1] + ans[-2] + 1 + (i + 1) / 2)
    return ans



dir = "/home/soumit/Thesis/NL-specification-driven-Code-Translation/Code-Translation-using-NL-Specification/debug_temp_evalplus_test/infered_type_HumanEval_130.txt"
with open(dir, "w") as __f__:

    inferred_types = infer_types_at_runtime(tri,4)
    for i in range(len(inferred_types)):
        print(f"{inferred_types[i][0]}: {inferred_types[i][1]}", file=__f__)
    ret_type = infer_return_type(tri,4)
    print(f"return: {ret_type}", file=__f__)
    __f__.close()

