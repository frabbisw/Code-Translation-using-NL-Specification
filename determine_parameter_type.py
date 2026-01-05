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