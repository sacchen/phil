from __future__ import annotations

import re

from .core import normalize_expression, relaxed_function_rewrites, reserved_name_suggestion


def should_print_wolfram_hint(exc: Exception) -> bool:
    text = str(exc).lower()
    if "cannot assign reserved name" in text:
        return False
    return True


def parse_explanation(expr: str, relaxed: bool, enabled: bool) -> str | None:
    if not enabled:
        return None
    normalized = normalize_expression(expr, relaxed=relaxed)
    return f"parsed as: {normalized}"


def relaxed_rewrite_messages(expr: str, relaxed: bool) -> list[str]:
    if not relaxed:
        return []
    seen: set[tuple[str, str]] = set()
    messages: list[str] = []
    for original, rewritten in relaxed_function_rewrites(expr):
        if (original, rewritten) in seen:
            continue
        seen.add((original, rewritten))
        messages.append(f"interpreted '{original}' as '{rewritten}'")
    return messages


def eq_has_top_level_comma(expr: str) -> bool:
    stripped = expr.strip()
    if not stripped.startswith("Eq("):
        return True
    inner = stripped[3:]
    if inner.endswith(")"):
        inner = inner[:-1]
    depth = 0
    for ch in inner:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            return True
    return False


def hint_for_error(message: str, expr: str | None = None, session_locals: dict | None = None) -> str | None:
    text = message.lower()
    if "unexpected eof" in text:
        if expr and ("/d" in expr or expr.strip().startswith("d(")):
            return "derivative syntax: d(expr, var) or d(sin(x))/dx or df(t)/dt"
        return "check missing closing ')' or unmatched quote"
    if "invalid syntax" in text:
        if expr:
            compact = re.sub(r"\s+", "", expr)
            if expr.strip().startswith("Eq(") and not eq_has_top_level_comma(expr):
                return "Eq syntax: Eq(lhs, rhs), for example Eq(d(y(x), x), y(x))"
            if "dsolve(" in compact and "eq(" not in compact:
                return "dsolve expects an equation: use dsolve(Eq(...), y(x))"
            if "\\frac" in expr:
                return "LaTeX fraction syntax: \\frac{numerator}{denominator}"
            if "d(" in compact or re.search(r"\bd[A-Za-z0-9_]+/d[A-Za-z0-9_]+\b", compact):
                return "derivative syntax: d(expr, var) or d(sin(x))/dx or df(t)/dt"
            if "matrix(" in compact.lower():
                return "matrix syntax: Matrix([[1,2],[3,4]])"
        return "check commas and brackets; try :examples for working patterns"
    if "cannot assign reserved name:" in text:
        if "cannot assign reserved name: f" in text:
            suggestion = reserved_name_suggestion("f", session_locals=session_locals)
            if suggestion:
                return f"'f' is reserved for function notation in ODEs; try '{suggestion}'"
            return "'f' is reserved for function notation in ODEs; choose another variable name (e.g. ff)"
        return "that name is reserved by phil internals; choose a different variable name"
    if "name '" in text and "is not defined" in text:
        if expr and ("/d" in expr or expr.strip().startswith("d")):
            return "derivative syntax: d(expr, var) or d(sin(x))/dx or df(t)/dt"
        return "use one of: x y z t pi e f and documented functions"
    if "dsolve() and classify_ode() only work with functions of one variable" in text:
        return "for ODEs, use function notation: y(x) and dsolve(Eq(d(y(x), x), ...), y(x))"
    if "data type not understood" in text:
        if expr and "matrix(" in expr.lower():
            return "matrix syntax: Matrix([[1,2],[3,4]])"
    if "blocked token" in text:
        return "remove blocked patterns like '__', ';', or newlines"
    if "empty expression" in text:
        return "enter a math expression, or use :examples"
    return None
