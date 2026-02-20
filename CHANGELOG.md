# Changelog

## 0.1.4 - 2026-02-20

- Add in-app guided tour commands (`:tutorial`, `:tour`, `:next`, `:repeat`, `:done`).
- Add `:ode` quick reference with `Eq(...)`/`dsolve(...)` templates.
- Improve syntax hints for malformed `Eq(...)`, missing `Eq(...)` in `dsolve(...)`, and LaTeX fraction syntax errors.
- Link and expand new-user onboarding with `TUTORIAL.md`.

## 0.1.3 - 2026-02-20

- Improve ODE input ergonomics for homework-style notation.
- Accept REPL inline options and `phil ...`-prefixed input lines.
- Normalize ODE shorthand forms such as `dy/dx = y`, `y' = y`, and `y'' + y = 0`.
- Normalize common LaTeX-style inputs including `\frac{dy}{dx}`, `$...$`, and `\sin/\cos/\ln/\sqrt`.
- Add targeted `dsolve` function-notation hints for `y(x)` usage.

## 0.1.0 - 2026-02-20

- Initial public release.
- Symbolic CLI calculator with exact arithmetic and core SymPy operations.
- Hardened parser configuration and input guardrails.
- Minimal terminal UX (`:h`, `:examples`, `:q`, `:x`) with actionable hints.
- Optional WolframAlpha fallback hint on evaluation errors.
- uv package layout, tests, and GitHub Actions CI.
