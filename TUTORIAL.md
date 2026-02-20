# phil Guided Tour

This is a step-by-step tour. Copy each command, run it, and compare with the expected output before moving on.

## Stop 1: Install and first answer

```bash
uv tool install philcalc
phil '2+2'
```

Expected:

```text
4
```

## Stop 2: Core homework operations

Run these one by one:

```bash
phil '1/3 + 1/6'
phil 'd(x^3 + 2*x, x)'
phil 'int(sin(x), x)'
phil 'solve(x^2 - 4, x)'
```

Expected shape:

- fraction result (`1/2`)
- derivative expression (`3*x**2 + 2`)
- integral expression (`-cos(x)`)
- roots list (`[-2, 2]`)

## Stop 3: Enter REPL for iterative work

Start:

```bash
phil
```

Now type exactly:

```text
phil> d(x^2, x)
phil> A = Matrix([[1,2],[3,4]])
phil> det(A)
phil> ans + 1
```

You should see:

- derivative output
- stored matrix echo
- determinant (`-2`)
- use of `ans` (`-1`)

Exit with:

```text
phil> :q
```

## Stop 4: Switch output style during work

One-shot mode:

```bash
phil --latex 'd(x^2, x)'
phil --format pretty 'Matrix([[1,2],[3,4]])'
```

Inside REPL, inline flags also work:

```text
phil> --latex d(x^2, x)
phil> phil --latex "d(x^2, x)"
```

## Stop 5: ODE input shortcuts (the important part)

These are equivalent first-order ODE inputs:

```bash
phil 'dy/dx = y'
phil "y' = y"
phil '\frac{dy}{dx} = y'
```

Second-order style:

```bash
phil "y'' + y = 0"
phil '\frac{d^2y}{dx^2} + y = 0'
```

## Stop 6: Solve an ODE explicitly

```bash
phil 'dsolve(Eq(d(y(x), x), y(x)), y(x))'
phil --latex 'dsolve(Eq(d(y(x), x), y(x)), y(x))'
```

If you see a `dsolve` error, use `y(x)` in both the equation and target function.

## Stop 7: Paste from LaTeX/markdown platforms

These paste-friendly forms are normalized:

```bash
phil '$d(x^2, x)$'
phil '\sin(x)^2 + \cos(x)^2'
phil '\sqrt{x} + \frac{1}{x}'
```

## Stop 8: When stuck

In one-shot mode:

```bash
phil :examples
```

In REPL:

```text
phil> :h
phil> :examples
```

For full command reference, see `/Users/goddess/foundry/sandbox/calc/README.md`.
