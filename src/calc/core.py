from __future__ import annotations

import re

from sympy import (
    Abs,
    E,
    Eq,
    Float,
    Function,
    Integer,
    N,
    Rational,
    Symbol,
    cos,
    diff,
    dsolve,
    exp,
    factorial,
    integrate,
    log,
    pi,
    simplify,
    sin,
    solve,
    sqrt,
    symbols,
    tan,
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
    return normalized


def evaluate(expression: str, relaxed: bool = False):
    _validate_expression(expression)
    normalized = normalize_expression(expression)
    transforms = RELAXED_TRANSFORMS if relaxed else TRANSFORMS
    parsed = parse_expr(
        normalized,
        local_dict=LOCALS_DICT,
        global_dict=GLOBAL_DICT,
        transformations=transforms,
        evaluate=True,
    )
    if isinstance(parsed, (list, tuple, dict)):
        return parsed
    return simplify(parsed)
