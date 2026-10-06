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

## Website

A browser version lives in `docs/` and is published with GitHub Pages. As
well as the periodic table it has Cells, Blood, Nervous System and Skeleton
tabs with clickable diagrams.

Preview it locally:

```bash
python3 -m http.server 8000 --directory docs
```

Then open http://localhost:8000/.

### Adding a topic

1. Draw each diagram as an SVG in `docs/diagrams/`. Wrap every clickable
   part in `<g data-part="some-id">`.
2. Write `docs/topics/<topic>.json` with the text for each part and the
   list of diagrams.
3. Add a tab button with `data-tab="<topic>"` to `docs/index.html`.
4. Run `pytest tests/test_topics.py`; it checks the drawings and text match.
