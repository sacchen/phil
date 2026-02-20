import calc.diagnostics as diagnostics


def test_should_print_wolfram_hint_policy():
    assert diagnostics.should_print_wolfram_hint(ValueError("cannot assign reserved name: f")) is False
    assert diagnostics.should_print_wolfram_hint(ValueError("different error")) is True


def test_parse_explanation_enabled_and_disabled():
    assert diagnostics.parse_explanation("sinx", relaxed=True, enabled=False) is None
    assert diagnostics.parse_explanation("sinx", relaxed=True, enabled=True) == "parsed as: sin(x)"


def test_relaxed_rewrite_messages_deduplicates_and_strict_mode():
    assert diagnostics.relaxed_rewrite_messages("sinx + sinx", relaxed=True) == ["interpreted 'sinx' as 'sin(x)'"]
    assert diagnostics.relaxed_rewrite_messages("sinx", relaxed=False) == []


def test_eq_has_top_level_comma_edge_cases():
    assert diagnostics.eq_has_top_level_comma("x + y") is True
    assert diagnostics.eq_has_top_level_comma("Eq(d(y(x), x), y(x))") is True
    assert diagnostics.eq_has_top_level_comma("Eq(d(y(x), x) y(x))") is False


def test_hint_for_error_additional_branches():
    assert "derivative syntax" in diagnostics.hint_for_error("Unexpected EOF while parsing", expr="d(x")
    assert "check commas and brackets" in diagnostics.hint_for_error("invalid syntax", expr="foo(")
    assert "try 'ff'" in diagnostics.hint_for_error(
        "cannot assign reserved name: f",
        session_locals={"ff": 1},
    )
    assert "derivative syntax" in diagnostics.hint_for_error("name 'a' is not defined", expr="d(a)")
    assert diagnostics.hint_for_error("data type not understood", expr="Matrix([1,2],[3,4])") == "matrix syntax: Matrix([[1,2],[3,4]])"
