import pytest

from calc.core import evaluate


def test_exact_arithmetic():
    assert str(evaluate("1/3 + 1/6")) == "1/2"


def test_derivative():
    assert str(evaluate("d(x^3 + 2*x, x)")) == "3*x**2 + 2"


def test_derivative_infers_single_symbol():
    assert str(evaluate("d(x^3 + 2*x)")) == "3*x**2 + 2"


def test_derivative_inference_ambiguous():
    with pytest.raises(ValueError, match="ambiguous variable"):
        evaluate("d(x*y)")


def test_derivative_inference_no_symbols():
    with pytest.raises(ValueError, match="no symbols found"):
        evaluate("d(42)")


def test_integral():
    assert str(evaluate("int(sin(x), x)")) == "-cos(x)"


def test_integral_infers_single_symbol():
    assert str(evaluate("int(sin(x))")) == "-cos(x)"


def test_integral_inference_ambiguous():
    with pytest.raises(ValueError, match="ambiguous variable"):
        evaluate("int(x + y)")


def test_integral_inference_no_symbols():
    with pytest.raises(ValueError, match="no symbols found"):
        evaluate("int(7)")


def test_solve():
    assert str(evaluate("solve(x^2 - 4, x)")) == "[-2, 2]"


def test_numeric_eval():
    assert str(evaluate("N(pi, 10)")) == "3.141592654"


def test_blocks_import_injection():
    with pytest.raises(Exception):
        evaluate('__import__("os").system("echo bad")')


def test_blocks_empty_expression():
    with pytest.raises(ValueError, match="empty expression"):
        evaluate("   ")


def test_blocks_dunder_access():
    with pytest.raises(ValueError, match="blocked token"):
        evaluate("x.__class__")


def test_blocks_long_expression():
    expr = "1+" * 2000 + "1"
    with pytest.raises(ValueError, match="expression too long"):
        evaluate(expr)


def test_blocks_newline_and_semicolon():
    with pytest.raises(ValueError, match="blocked token"):
        evaluate("1+2\n3")
    with pytest.raises(ValueError, match="blocked token"):
        evaluate("1+2;3")


def test_normalizes_ln_and_unicode_minus():
    assert str(evaluate("ln(x)")) == "log(x)"
    assert str(evaluate("2−1")) == "1"


def test_relaxed_parses_braces_ln_and_implicit_multiplication():
    expr = "(1 - 25e^5)e^{-5t} + (25e^5 - 1)t e^{-5t} + t e^{-5t} ln(t)"
    out = str(evaluate(expr, relaxed=True))
    assert "exp(-5*t)" in out
    assert "log(t)" in out


def test_relaxed_parses_second_long_expression():
    expr = "(854/2197)e^{8t}+(1343/2197)e^{-5t}+((9/26)t^2 -(9/169)t)e^{8t}"
    out = str(evaluate(expr, relaxed=True))
    assert "exp(" in out
    assert "exp(-5*t)" in out
