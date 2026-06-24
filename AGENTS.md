# AGENTS.md

## Coding Style

- Keep lines under 80 characters.
- Prefer single quotes for string literals.
- Prefer f-strings over other formatting methods.
- Use triple double quotes for docstrings.
- In multi-line docstrings, place the opening """ on its own line.
- Make sure that:
  - Private functions (name starting with `_`) are only used internally within
    a module
  - Only functions that are used across different modules are public

## Before Finalizing

For any non-trivial change:

1. Re-read all modified files.
2. Simplify code where possible.
3. Re-run relevant tests and checks.
4. Fix issues locally rather than relying on CI.

Required checks:

```bash
flake8 <modified_python_files> && sourcery review <modified_files>
```

## Commits

- Keep commit messages short.
- Follow the style of recent commits in the repository.
- Use command line `git`.

## Local Setup

Run once per clone:

```bash
scripts/setup_local_hooks.sh
```

This installs the pre-commit hook used to enforce local style checks.
