import pytest
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st

from calc.core import MAX_EXPRESSION_CHARS, evaluate


@pytest.mark.unit
@given(st.integers(min_value=-10_000, max_value=10_000), st.integers(min_value=-10_000, max_value=10_000))
def test_property_integer_addition_matches_python(a: int, b: int):
    expr = f"{a}+{b}"
    assert str(evaluate(expr)) == str(a + b)


@pytest.mark.unit
@given(st.integers(min_value=-50, max_value=50))
def test_property_derivative_inference_matches_explicit(coef: int):
    inferred = str(evaluate(f"d({coef}*x^2 + x)"))
    explicit = str(evaluate(f"d({coef}*x^2 + x, x)"))
    assert inferred == explicit


@pytest.mark.unit
@settings(max_examples=100)
@given(
    head=st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_size=0, max_size=40),
    blocked=st.sampled_from(["__", ";", "\n", "\r"]),
    tail=st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_size=0, max_size=40),
)
def test_property_blocked_tokens_are_rejected(head: str, blocked: str, tail: str):
    with pytest.raises(ValueError, match="blocked token|empty expression"):
        evaluate(f"{head}{blocked}{tail}")


@pytest.mark.unit
@settings(max_examples=50)
@given(
    suffix=st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_size=1, max_size=100)
)
def test_property_expressions_above_max_length_are_rejected(suffix: str):
    expr = "x" * (MAX_EXPRESSION_CHARS + len(suffix))
    with pytest.raises(ValueError, match="expression too long"):
        evaluate(expr)
