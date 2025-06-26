import math

def calculate_expression(expr):
    """Safely evaluate a basic math expression."""
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    allowed_names['abs'] = abs
    code = compile(expr, "<string>", "eval")
    for name in code.co_names:
        if name not in allowed_names:
            raise NameError(f"Use of '{name}' not allowed.")
    return round(eval(code, {"__builtins__": {}}, allowed_names), 2) 