import runpy
from types import SimpleNamespace

import pytest

import calc.cli as cli


def test_parse_options_help_exits(capsys):
    with pytest.raises(SystemExit):
        cli._parse_options(["--help"])
    out = capsys.readouterr().out
    assert "usage:" in out


def test_parse_options_unknown_raises():
    with pytest.raises(ValueError, match="unknown option"):
        cli._parse_options(["--wat"])


def test_parse_options_flags():
    latex_output, relaxed, always_wa, copy_wa, rest = cli._parse_options(
        ["--latex", "--strict", "--wa", "--copy-wa", "2+2"]
    )
    assert latex_output is True
    assert relaxed is False
    assert always_wa is True
    assert copy_wa is True
    assert rest == ["2+2"]


def test_parse_options_double_dash_and_single_dash_literal():
    _, _, _, _, rest = cli._parse_options(["--", "--not-an-option"])
    assert rest == ["--not-an-option"]
    _, _, _, _, rest = cli._parse_options(["-1"])
    assert rest == ["-1"]


def test_hint_for_error_messages():
    assert "missing closing" in cli._hint_for_error("Unexpected EOF while parsing")
    assert "documented functions" in cli._hint_for_error("name 'a' is not defined")
    assert "blocked patterns" in cli._hint_for_error("blocked token in expression")
    assert "enter a math expression" in cli._hint_for_error("empty expression")
    assert cli._hint_for_error("different error") is None


def test_is_complex_expression_heuristics():
    assert cli._is_complex_expression("x" * 40) is True
    assert cli._is_complex_expression("d(x^2, x)") is True
    assert cli._is_complex_expression("2+2") is False


def test_format_result_latex():
    assert cli._format_result("x", latex_output=False) == "x"
    assert cli._format_result(2, latex_output=True) == "2"


def test_format_clickable_link_tty(monkeypatch):
    monkeypatch.setattr(cli.sys.stderr, "isatty", lambda: True)
    monkeypatch.setenv("TERM", "xterm-256color")
    out = cli._format_clickable_link("Open", "https://example.com")
    assert "https://example.com" in out
    assert "\033]8;;" in out


def test_copy_to_clipboard_success(monkeypatch):
    monkeypatch.setattr(cli.shutil, "which", lambda name: "/bin/pbcopy" if name == "pbcopy" else None)
    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    assert cli._copy_to_clipboard("abc") is True


def test_copy_to_clipboard_failure(monkeypatch):
    monkeypatch.setattr(cli.shutil, "which", lambda name: None)
    assert cli._copy_to_clipboard("abc") is False


def test_copy_to_clipboard_exception_then_fallback(monkeypatch):
    monkeypatch.setattr(cli.shutil, "which", lambda name: "/bin/tool" if name == "pbcopy" else None)

    def boom(*args, **kwargs):
        raise RuntimeError("clipboard error")

    monkeypatch.setattr(cli.subprocess, "run", boom)
    assert cli._copy_to_clipboard("abc") is False


def test_latest_pypi_version_success(monkeypatch):
    class DummyResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"info":{"version":"9.9.9"}}'

    monkeypatch.setattr(cli, "urlopen", lambda *a, **k: DummyResponse())
    assert cli._latest_pypi_version() == "9.9.9"


def test_latest_pypi_version_failure(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("offline")

    monkeypatch.setattr(cli, "urlopen", boom)
    assert cli._latest_pypi_version() is None


def test_print_update_status_dev(monkeypatch, capsys):
    monkeypatch.setattr(cli, "VERSION", "dev")
    cli._print_update_status()
    out = capsys.readouterr().out
    assert "local checkout" in out
    assert "install latest local changes" in out


def test_print_update_status_up_to_date(monkeypatch, capsys):
    monkeypatch.setattr(cli, "VERSION", "1.2.3")
    monkeypatch.setattr(cli, "_latest_pypi_version", lambda: "1.2.3")
    cli._print_update_status()
    out = capsys.readouterr().out
    assert "up to date" in out


def test_print_update_status_update_available(monkeypatch, capsys):
    monkeypatch.setattr(cli, "VERSION", "1.2.3")
    monkeypatch.setattr(cli, "_latest_pypi_version", lambda: "2.0.0")
    cli._print_update_status()
    out = capsys.readouterr().out
    assert "update available" in out


def test_print_update_status_latest_unavailable(monkeypatch, capsys):
    monkeypatch.setattr(cli, "VERSION", "1.2.3")
    monkeypatch.setattr(cli, "_latest_pypi_version", lambda: None)
    cli._print_update_status()
    out = capsys.readouterr().out
    assert "unavailable" in out


def test_calc_version_package_missing(monkeypatch):
    def boom(_):
        raise cli.PackageNotFoundError

    monkeypatch.setattr(cli, "package_version", boom)
    assert cli._calc_version() == "dev"


def test_run_one_shot_success(monkeypatch, capsys):
    monkeypatch.setattr(cli, "evaluate", lambda expr, relaxed: 4)
    rc = cli.run(["2+2"])
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out.strip().endswith("4")


def test_run_one_shot_error(monkeypatch, capsys):
    def boom(expr, relaxed):
        raise ValueError("empty expression")

    monkeypatch.setattr(cli, "evaluate", boom)
    rc = cli.run(["2+2"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "E: empty expression" in captured.err
    assert "try WolframAlpha" in captured.err


def test_run_repl_uses_strict_flag(monkeypatch, capsys):
    calls = []
    inputs = iter(["2x", ":q"])

    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    def fake_eval(expr, relaxed):
        calls.append(relaxed)
        return "ok"

    monkeypatch.setattr(cli, "evaluate", fake_eval)
    rc = cli.run(["--strict"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "ok" in captured.out
    assert calls == [False]


def test_run_help_returns_zero(capsys):
    rc = cli.run(["--help"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "usage:" in out


def test_run_shortcut_commands(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_print_update_status", lambda: print("status"))
    assert cli.run([":examples"]) == 0
    assert cli.run([":version"]) == 0
    assert cli.run([":update"]) == 0
    out = capsys.readouterr().out
    assert "examples:" in out
    assert "calc v" in out
    assert "status" in out


def test_run_one_shot_prints_wa_when_forced(monkeypatch, capsys):
    monkeypatch.setattr(cli, "evaluate", lambda expr, relaxed: 4)
    monkeypatch.setattr(cli, "_print_wolfram_hint", lambda expr, copy_link=False: print("WA", file=cli.sys.stderr))
    rc = cli.run(["--wa", "2+2"])
    err = capsys.readouterr().err
    assert rc == 0
    assert "WA" in err


def test_run_repl_empty_then_command(monkeypatch, capsys):
    inputs = iter(["", ":h", ":q"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    rc = cli.run([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "repl commands:" in out


def test_run_repl_error_path(monkeypatch, capsys):
    inputs = iter(["2+2", ":q"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    def boom(expr, relaxed):
        raise ValueError("empty expression")

    monkeypatch.setattr(cli, "evaluate", boom)
    rc = cli.run([])
    err = capsys.readouterr().err
    assert rc == 0
    assert "E: empty expression" in err


def test_print_wolfram_hint_copy_branches(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_copy_to_clipboard", lambda text: True)
    cli._print_wolfram_hint("2+2", copy_link=True)
    err = capsys.readouterr().err
    assert "copied to clipboard" in err

    monkeypatch.setattr(cli, "_copy_to_clipboard", lambda text: False)
    cli._print_wolfram_hint("2+2", copy_link=True)
    err = capsys.readouterr().err
    assert "clipboard copy unavailable" in err


def test_handle_repl_commands(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_print_update_status", lambda: print("status"))
    assert cli._handle_repl_command(":h") is True
    assert cli._handle_repl_command(":examples") is True
    assert cli._handle_repl_command(":version") is True
    assert cli._handle_repl_command(":check") is True
    assert cli._handle_repl_command(":wat") is True
    assert cli._handle_repl_command("2+2") is False
    err = capsys.readouterr().err
    assert "unknown command" in err


def test_main_module_executes():
    with pytest.raises(SystemExit):
        runpy.run_module("calc.__main__", run_name="__main__")


def test_cli_module_main_executes():
    with pytest.raises(SystemExit):
        runpy.run_module("calc.cli", run_name="__main__")
