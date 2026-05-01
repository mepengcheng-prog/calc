"""Safe mathematical expression evaluator for the calculator."""

import math
import ast
import operator as op

# supported operators and their Python equivalents
OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.Mod: op.mod,
}

CONSTANTS = {
    "π": math.pi,
    "pi": math.pi,
    "e": math.e,
    "PI": math.pi,
}

# --- Trig mode: DEG (default) or RAD ---
_trig_deg = True


def set_trig_mode(deg: bool) -> None:
    global _trig_deg
    _trig_deg = deg


def is_deg_mode() -> bool:
    return _trig_deg


def _sin(x):
    return math.sin(math.radians(x)) if _trig_deg else math.sin(x)


def _cos(x):
    return math.cos(math.radians(x)) if _trig_deg else math.cos(x)


def _tan(x):
    return math.tan(math.radians(x)) if _trig_deg else math.tan(x)


def _asin(x):
    return math.degrees(math.asin(x)) if _trig_deg else math.asin(x)


def _acos(x):
    return math.degrees(math.acos(x)) if _trig_deg else math.acos(x)


def _atan(x):
    return math.degrees(math.atan(x)) if _trig_deg else math.atan(x)


FUNCTIONS = {
    "sin": _sin,
    "cos": _cos,
    "tan": _tan,
    "asin": _asin,
    "acos": _acos,
    "atan": _atan,
    "log": math.log10,
    "ln": math.log,
    "sqrt": math.sqrt,
    "cbrt": lambda x: x ** (1 / 3),
    "abs": abs,
    "exp": math.exp,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,
}


def _eval_expr(node):
    """Evaluate an AST node safely."""
    if isinstance(node, ast.Expression):
        return _eval_expr(node.body)

    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.UnaryOp):
        return OPERATORS[type(node.op)](_eval_expr(node.operand))

    if isinstance(node, ast.BinOp):
        return OPERATORS[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))

    if isinstance(node, ast.Call):
        func_name = node.func.id if isinstance(node.func, ast.Name) else None
        if func_name not in FUNCTIONS:
            raise ValueError(f"Unknown function: {func_name}")
        args = [_eval_expr(arg) for arg in node.args]
        return FUNCTIONS[func_name](*args)

    if isinstance(node, ast.Name):
        if node.id in CONSTANTS:
            return CONSTANTS[node.id]
        raise ValueError(f"Unknown variable: {node.id}")

    raise ValueError(f"Unsupported syntax: {type(node).__name__}")


def evaluate(expression: str) -> str:
    """Evaluate a mathematical expression string. Returns result string."""
    expression = expression.strip()
    if not expression:
        return ""

    # replace display symbols with Python equivalents
    expr = (
        expression.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("²", "**2")
        .replace("³", "**3")
        .replace("π", str(math.pi))
    )

    try:
        tree = ast.parse(expr, mode="eval")
        result = _eval_expr(tree)
        if isinstance(result, float):
            if result == int(result) and abs(result) < 1e15:
                return str(int(result))
            return f"{result:.10g}"
        return str(result)
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError):
        return "Error"
    except OverflowError:
        return "Overflow"
