@python.md

# cube_cli — Claude Project Notes

## What This Project Is
A Python CLI application that wraps `cube_model` to provide
command-line interaction with a cube puzzle model.

## Repo Layout

    src/cube_cli/   # application source
    tests/           # pytest test suite mirroring src layout
    pyproject.toml   # Poetry config, deps, mypy & pytest settings

## Running Things
Do NOT use `poetry run` to execute commands. Use `python -m`:

Type-check:

    python -m mypy --strict src/ tests/

Run tests:

    python -m pytest

Run the CLI directly:

    python -m cube_cli.main

## Dependencies
Managed by Poetry in `pyproject.toml`. Do not edit that file by hand
for deps; document the intended `poetry add` command instead and let
the user run it.

## Editor & Shell
- Editor: vim
- Shell scripts: bash
- On Termux, do not use `poetry run` or `pipx`
