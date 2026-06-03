# Periodic Table GUI — Design Spec

**Date:** 2026-06-03
**Status:** Approved (brainstorming phase)
**Author:** brainstorming session

## Overview

A desktop GUI application that displays the periodic table of elements. Users can click any element to open a detail popup, and from that popup open a second window showing a Bohr-model visualization of the atom.

## Goals

- Display all 118 elements in the canonical periodic-table grid layout.
- Allow clicking an element to view its detailed properties in a popup window.
- From the detail popup, allow the user to view a static Bohr-model diagram of the atom.
- Allow filtering/highlighting elements by name, symbol, or atomic number.
- Run entirely offline with no external dependencies beyond the Python standard library.

## Non-goals (v1)

- Animated atomic models or electron orbital visualizations.
- Isotope, ion, or compound information.
- Plots, trends, or comparative analytics.
- Internationalization, accessibility audit, or theming.
- Packaging as a standalone `.app`/`.exe`.
- Persistence (favorites, history, user settings).
- Network calls of any kind.

## Tech Stack

- **Python** 3.10+ (for `dataclass(slots=True)`, `match`-style typing if needed).
- **Tkinter** (standard library) for all GUI rendering.
- **No external dependencies.** Static dataset is bundled in source.

## Architecture

### File Layout

```
main.py
periodic_table/
    __init__.py
    model.py            # Element dataclass, Category enum
    data.py             # ELEMENTS: list[Element] — static dataset of 118
    categories.py       # CATEGORY_COLORS: dict[Category, str]
    placement.py        # placement_for(element) -> (row, col)
    shells.py           # fill_shells(Z) -> list[int]
    search.py           # match(query, element) -> bool
    views/
        __init__.py
        grid_view.py        # PeriodicGridView(tk.Frame)
        search_bar.py       # SearchBar(tk.Frame)
        detail_window.py    # ElementDetailWindow(tk.Toplevel)
        atom_view.py        # AtomWindow(tk.Toplevel)
tests/
    test_data.py
    test_placement.py
    test_shells.py
    test_search.py
    test_smoke_gui.py
```

### Layout

```
+--------------------------------------------------+
| SearchBar                                        |
+--------------------------------------------------+
|                                                  |
|  PeriodicGridView (18 cols x 7 main rows)        |
|                                                  |
|  Lanthanide strip (La..Lu)                       |
|  Actinide strip (Ac..Lr)                         |
+--------------------------------------------------+

Click element  -->  ElementDetailWindow (Toplevel)
                        |
                        +-- [Show atom] button -->  AtomWindow (Toplevel)
```

## Components

### `model.Element`

```python
@dataclass(frozen=True, slots=True)
class Element:
    atomic_number: int
    symbol: str
    name: str
    mass: float
    period: int
    group: int | None         # None for lanthanides/actinides
    category: Category
    electron_config: str
    electronegativity: float | None
    phase: str                # "solid" | "liquid" | "gas" | "unknown"
```

### `model.Category` (enum)

`ALKALI_METAL`, `ALKALINE_EARTH`, `TRANSITION_METAL`, `POST_TRANSITION`,
`METALLOID`, `NONMETAL`, `HALOGEN`, `NOBLE_GAS`, `LANTHANIDE`, `ACTINIDE`, `UNKNOWN`.

### `data.ELEMENTS`

Static `list[Element]` of 118 elements built at module import. Source: IUPAC reference values. No I/O. Read-only.

### `placement.placement_for(element) -> (row, col)`

Pure function. Returns 0-indexed `(row, col)` for the unified table grid.

Convention:
- Rows `0..6`: main 7-period grid, cols `0..17`.
- Row `7`: lanthanide strip (La..Lu), cols `0..14`. La → `(7, 0)`, Lu → `(7, 14)`.
- Row `8`: actinide strip (Ac..Lr), cols `0..14`. Ac → `(8, 0)`, Lr → `(8, 14)`.
- Placeholder cells `*` at `(5, 2)` and `**` at `(6, 2)` mark where the La/Ac series belong in the main grid; they are non-clickable labels, not elements.

`PeriodicGridView` uses this single convention for `tk.grid()` placement; no separate sub-grids needed.

### `shells.fill_shells(Z) -> list[int]`

Pure function. Returns electron count per Bohr shell using simple shell-capacity fill order (not Aufbau — intentionally simplified for visualization).

```python
def fill_shells(Z: int) -> list[int]:
    capacities = [2, 8, 18, 32, 32, 18, 8]
    remaining = Z
    result = []
    for cap in capacities:
        n = min(cap, remaining)
        if n == 0:
            break
        result.append(n)
        remaining -= n
    return result
```

Examples:
- `Z=1`  → `[1]`
- `Z=2`  → `[2]`
- `Z=10` → `[2, 8]`
- `Z=18` → `[2, 8, 8]`
- `Z=118` → `[2, 8, 18, 32, 32, 18, 8]`

### `search.match(query, element) -> bool`

Pure function. Case-insensitive. Matches if:
- `query` is empty, OR
- `element.symbol.lower() == query.lower()`, OR
- `element.name.lower().startswith(query.lower())`, OR
- `query` parses as `int` and equals `element.atomic_number`.

### `views.grid_view.PeriodicGridView(tk.Frame)`

Builds 118 `tk.Button` cells (one per element) plus two placeholder cells for La/Ac series markers. Each button:
- Label: symbol + small atomic number.
- Background: `CATEGORY_COLORS[element.category]`.
- Command: invokes `on_select(element)` (callback passed in constructor).

Exposes `highlight(query: str)` → for every cell, if `match(query, element)` keep original color; otherwise set background to `"#dddddd"`. Empty query restores all.

### `views.search_bar.SearchBar(tk.Frame)`

`tk.Entry` bound to `StringVar`. `trace_add("write", ...)` calls `on_change(query)` callback.

### `views.detail_window.ElementDetailWindow(tk.Toplevel)`

Created on element click. Shows all `Element` fields as `Label` rows. Missing optional fields render as `"—"`. Contains a `tk.Button("Show atom")` that opens `AtomWindow(self, element)`. Calls `transient(parent)`. Closing parent closes this window (Tk default).

### `views.atom_view.AtomWindow(tk.Toplevel)`

Contains a single `tk.Canvas` (600x600). Renders Bohr model:

1. Compute `shells = fill_shells(element.atomic_number)`. Let `K = len(shells)`.
2. Center `(300, 300)`. Draw filled nucleus circle radius 20; label `symbol` + `Z`.
3. For shell `i` in `1..K`:
   - Shell radius `r_i = 30 + i * (250 // K)`.
   - Draw circle outline at radius `r_i`.
   - For electron `k` in `0..shells[i-1]-1`:
     - `theta = 2 * pi * k / shells[i-1]`
     - `x = 300 + r_i * cos(theta)`, `y = 300 + r_i * sin(theta)`
     - Draw filled circle radius 4 at `(x, y)`.

Static render — no animation.

## Data Flow

1. `main.py` imports `ELEMENTS` (built once at module load).
2. `main.py` constructs `SearchBar`, `PeriodicGridView` in a `tk.Tk` root.
3. `SearchBar(on_change=grid_view.highlight)`.
4. `PeriodicGridView(on_select=lambda e: ElementDetailWindow(root, e))`.
5. `ElementDetailWindow` "Show atom" button → `AtomWindow(self, element)`.

No global state. No mutation of `ELEMENTS`. All views read from immutable dataclasses.

## Error Handling

- **Boundary: search input.** Always a string. Empty/whitespace = reset highlight. Non-numeric input simply fails the `int()` branch silently. Never crashes.
- **Internal lookups.** Trust the static dataset. No defensive try/except around dict/list access.
- **Missing optional fields** (e.g. electronegativity for noble gases): render as `"—"` in detail window.
- **No file or network I/O** → no IO error paths to handle.

## Testing

### Unit (pure functions only — no GUI)

- `test_data.py`
  - Asserts `len(ELEMENTS) == 118`.
  - Atomic numbers are exactly `{1..118}`, no duplicates.
  - Every element has non-empty `symbol`, `name`, valid `period in 1..7`, valid `category`.
  - `group` is `None` only for lanthanides/actinides; otherwise `1..18`.
- `test_placement.py`
  - Hydrogen → `(0, 0)`.
  - Helium → `(0, 17)`.
  - Carbon → `(1, 13)`.
  - Lanthanum → lanthanide-strip slot 0.
  - Lawrencium → actinide-strip slot 14.
- `test_shells.py`
  - `fill_shells(1) == [1]`
  - `fill_shells(2) == [2]`
  - `fill_shells(10) == [2, 8]`
  - `fill_shells(18) == [2, 8, 8]`
  - `fill_shells(118) == [2, 8, 18, 32, 32, 18, 8]`
  - `sum(fill_shells(Z)) == Z` for all `Z in 1..118`.
- `test_search.py`
  - Empty query matches all.
  - `"Na"` matches Sodium (symbol exact).
  - `"sod"` matches Sodium (name prefix, case-insensitive).
  - `"11"` matches Sodium (atomic number).
  - `"xyz"` matches nothing.

### Smoke (GUI)

- `test_smoke_gui.py`
  - Construct `tk.Tk`, call `root.withdraw()`.
  - Instantiate `SearchBar`, `PeriodicGridView`, an `ElementDetailWindow(root, ELEMENTS[0])`, and an `AtomWindow(root, ELEMENTS[117])`.
  - Assert no exceptions raised.
  - Destroy root.
  - Guarded by `pytest.importorskip("tkinter")` and a try/except around `tk.Tk()` to skip on headless CI where Tk cannot open a display.

## Open Questions / Future Work

- Add a list/spreadsheet alternate view (sortable `ttk.Treeview`).
- Add trend plots (atomic radius vs Z, electronegativity vs Z) on a Canvas.
- Animated electron motion in `AtomWindow`.
- Bundle as a single-file executable via PyInstaller.
- Dark mode / theming.