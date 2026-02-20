from __future__ import annotations

import re

from sympy import (
    Abs,
    E,
    Eq,
    Float,
    Function,
    Integer,
    Matrix,
    N,
    Rational,
    Symbol,
    cos,
    diff,
    dsolve,
    eye,
    exp,
    factorial,
    integrate,
    log,
    ones,
    pi,
    simplify,
    sin,
    solve,
    sqrt,
    symbols,
    tan,
    zeros,
)
from sympy.parsing.sympy_parser import (
    auto_number,
    convert_xor,
    factorial_notation,
    implicit_multiplication_application,
    parse_expr,
)

x, y, z, t = symbols("x y z t")
f = Function("f")
yf = Function("y")


def _infer_variable(expr, op_name: str):
    free_symbols = sorted(expr.free_symbols, key=str)
    if len(free_symbols) == 1:
        return free_symbols[0]
    if not free_symbols:
        raise ValueError(f"{op_name} requires a variable (no symbols found)")
    raise ValueError(f"ambiguous variable for {op_name}; pass one explicitly")


def _d(expr, var=None):
    if var is None:
        var = _infer_variable(expr, "d(expr)")
    return diff(expr, var)


def _int(expr, var=None):
    if var is None:
        var = _infer_variable(expr, "int(expr)")
    return integrate(expr, var)

LOCALS_DICT = {
    "x": x,
    "y": y,
    "z": z,
    "t": t,
    "pi": pi,
    "e": E,
    "f": f,
    "yf": yf,
    "d": _d,
    "int": _int,
    "solve": solve,
    "dsolve": dsolve,
    "Eq": Eq,
    "N": N,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "exp": exp,
    "log": log,
    "sqrt": sqrt,
    "abs": Abs,
    "Matrix": Matrix,
    "eye": eye,
    "zeros": zeros,
    "ones": ones,
    "det": lambda matrix: matrix.det(),
    "inv": lambda matrix: matrix.inv(),
    "rank": lambda matrix: matrix.rank(),
    "eigvals": lambda matrix: matrix.eigenvals(),
}

# parse_expr internally uses eval. Keep globals minimal and disable builtins.
GLOBAL_DICT = {
    "__builtins__": {},
    "Integer": Integer,
    "Float": Float,
    "Rational": Rational,
    "Symbol": Symbol,
    "factorial": factorial,
}

TRANSFORMS = (auto_number, factorial_notation, convert_xor)
RELAXED_TRANSFORMS = (
    auto_number,
    factorial_notation,
    convert_xor,
    implicit_multiplication_application,
)
MAX_EXPRESSION_CHARS = 2000
BLOCKED_PATTERN = re.compile(r"(__|;|\n|\r)")
ASSIGNMENT_PATTERN = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(.+)\s*$")
EQUALITY_PATTERN = re.compile(r"(?<![<>=!])=(?!=)")
LEIBNIZ_SIMPLE_PATTERN = re.compile(
    r"\bd\s*([A-Za-z][A-Za-z0-9_]*(?:\([^()]*\))?)\s*/\s*d\s*([A-Za-z][A-Za-z0-9_]*)\b"
)
ODE_SHORT_EQ_PATTERN = re.compile(
    r"^\s*d\s*([A-Za-z][A-Za-z0-9_]*)\s*/\s*d\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$"
)


def _dependent_expr(dep: str, var: str) -> str:
    if dep == "y":
        return f"yf({var})"
    if dep == "f":
        return f"f({var})"
    return dep


def _replace_bare_dependent(rhs: str, dep: str, dep_expr: str) -> str:
    return re.sub(rf"\b{re.escape(dep)}\b(?!\s*\()", dep_expr, rhs)


def _validate_expression(expression: str) -> None:
    if not expression.strip():
        raise ValueError("empty expression")
    if len(expression) > MAX_EXPRESSION_CHARS:
        raise ValueError(f"expression too long (max {MAX_EXPRESSION_CHARS} chars)")
    if BLOCKED_PATTERN.search(expression):
        raise ValueError("blocked token in expression")


def normalize_expression(expression: str) -> str:
    normalized = expression.replace("{", "(").replace("}", ")").replace("−", "-")
    # Accept common math shorthand from CAS/calculator input style.
    normalized = re.sub(r"\bln\s*\(", "log(", normalized)
    # Treat y(x) as an ODE function call while keeping y available as a symbol.
    normalized = re.sub(r"\by\s*\(", "yf(", normalized)
    ode_match = ODE_SHORT_EQ_PATTERN.match(normalized)
    if ode_match:
        dep, var, rhs = ode_match.group(1), ode_match.group(2), ode_match.group(3)
        dep_expr = _dependent_expr(dep, var)
        rhs = _replace_bare_dependent(rhs, dep, dep_expr)
        return f"Eq(d({dep_expr}, {var}), {rhs})"
    # Support Leibniz-style shorthand: d(expr)/dvar -> d(expr, var)
    normalized = re.sub(
        r"\bd\s*\((.+?)\)\s*/\s*d\s*([A-Za-z][A-Za-z0-9_]*)\b",
        r"d(\1, \2)",
        normalized,
    )
    normalized = LEIBNIZ_SIMPLE_PATTERN.sub(
        lambda m: f"d({_dependent_expr(m.group(1), m.group(2))}, {m.group(2)})",
        normalized,
    )
    if EQUALITY_PATTERN.search(normalized) and not ASSIGNMENT_PATTERN.match(normalized):
        lhs, rhs = EQUALITY_PATTERN.split(normalized, maxsplit=1)
        lhs = lhs.strip()
        rhs = rhs.strip()
        if lhs and rhs:
            normalized = f"Eq({lhs}, {rhs})"
    return normalized


def _evaluate_parsed(parsed, simplify_output: bool):
    if isinstance(parsed, (list, tuple, dict)):
        return parsed
    if simplify_output:
        return simplify(parsed)
    return parsed


def evaluate(
    expression: str,
    relaxed: bool = False,
    session_locals: dict | None = None,
    simplify_output: bool = True,
):
    _validate_expression(expression)
    normalized = normalize_expression(expression)
    transforms = RELAXED_TRANSFORMS if relaxed else TRANSFORMS
    local_dict = dict(LOCALS_DICT)
    if session_locals:
        local_dict.update(session_locals)

    match = ASSIGNMENT_PATTERN.match(normalized)
    if match:
        name, rhs = match.group(1), match.group(2)
        if name in LOCALS_DICT:
            raise ValueError(f"cannot assign reserved name: {name}")
        parsed_rhs = parse_expr(
            rhs,
            local_dict=local_dict,
            global_dict=GLOBAL_DICT,
            transformations=transforms,
            evaluate=True,
        )
        result = _evaluate_parsed(parsed_rhs, simplify_output=simplify_output)
        if session_locals is not None:
            session_locals[name] = result
            session_locals["ans"] = result
        return result

    parsed = parse_expr(
        normalized,
        local_dict=local_dict,
        global_dict=GLOBAL_DICT,
        transformations=transforms,
        evaluate=True,
    )
    result = _evaluate_parsed(parsed, simplify_output=simplify_output)
    if session_locals is not None:
        session_locals["ans"] = result
    return result
