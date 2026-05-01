# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

科学计算器 — Kivy-based scientific calculator targeting Android.

## Commands

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate   # Git Bash
.venv\Scripts\activate          # cmd/PowerShell

# Install
pip install -e .
pip install -e ".[dev]"         # with test/lint tools

# Run locally (desktop)
python -m src.calculator.main

# Run tests
pytest
pytest tests/test_engine.py::test_basic_arithmetic -v

# Lint / format / type
ruff check .
ruff format .
mypy src/

# Package for Android (requires WSL / Linux / macOS)
# buildozer android debug deploy run
```

## Structure

```
D:\my
├── src/calculator/
│   ├── main.py           # entry point: run `python -m src.calculator.main`
│   ├── app.py            # CalculatorApp — Kivy App class, button handling
│   ├── engine.py         # safe expression evaluator (AST-based, no eval)
│   ├── calculator.kv     # Kivy UI layout (kvlang)
│   └── __init__.py
├── tests/
│   ├── test_engine.py
│   └── __init__.py
├── buildozer.spec        # Android packaging config
├── pyproject.toml
└── .gitignore
```

## Key design

- **engine.py** uses `ast.parse` + recursive tree walk — no `eval()` — safe for arbitrary input.
- **calculator.kv** has a toggle-able scientific button grid (sin/cos/tan/log/√/π etc.) and a basic number pad.
- `buildozer.spec` targets Android API 34, portrait only.
- The KV file references `CalculatorApp`, so the class name must match exactly.
