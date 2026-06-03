# Periodic Table

A small Tkinter desktop app that displays the periodic table of elements.
Click an element for details; from the detail popup, click **Show atom** to
view a static Bohr-model diagram.

## Requirements

- Python 3.10+
- Tkinter (bundled with the standard CPython distribution)

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Run

```bash
.venv/bin/python main.py
```

## Tests

```bash
.venv/bin/pytest
```

The GUI smoke test is skipped on systems where Tk cannot open a display.
