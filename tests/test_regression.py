import pytest

from calc.core import evaluate


@pytest.mark.regression
@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("d(sin(x))/dx", "cos(x)"),
        ("df(t)/dt", "Derivative(f(t), t)"),
        ("dy/dx = y", "Eq(y(x), Derivative(y(x), x))"),
        ("det(Matrix([[1,2],[3,4]]))", "-2"),
        ("rank(Matrix([[1,2],[2,4]]))", "1"),
        ("int(sin(x))", "-cos(x)"),
    ],
)
def test_regression_core_cases(expr: str, expected: str):
    assert str(evaluate(expr, relaxed=True)) == expected


@pytest.mark.regression
def test_regression_no_simplify_keeps_structure():
    out = str(evaluate("sin(x)^2 + cos(x)^2", simplify_output=False))
    assert out == "sin(x)**2 + cos(x)**2"
