# Periodic Table GUI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Tkinter desktop app that displays the periodic table; click an element to open a detail popup; the popup has a "Show atom" button that opens a Bohr-model diagram.

**Architecture:** Pure-Python `periodic_table` package. Pure logic modules (`model`, `shells`, `placement`, `search`, `data`, `categories`) are TDD-tested without touching Tk. Tk view modules (`grid_view`, `search_bar`, `detail_window`, `atom_view`) are wired together in `main.py`. No external dependencies. Static element dataset loaded once at import.

**Tech Stack:**
- Python 3.10+
- Tkinter (standard library)
- pytest (dev only)

**Spec:** `docs/superpowers/specs/2026-06-03-periodic-table-design.md`

---

## File Structure

**Create:**
- `periodic_table/__init__.py`
- `periodic_table/model.py` — `Element` dataclass, `Category` enum
- `periodic_table/categories.py` — `CATEGORY_COLORS` mapping
- `periodic_table/shells.py` — `fill_shells(Z) -> list[int]`
- `periodic_table/placement.py` — `placement_for(element) -> (row, col)` + placeholder constants
- `periodic_table/search.py` — `match(query, element) -> bool`
- `periodic_table/data.py` — `ELEMENTS: list[Element]` (118 entries)
- `periodic_table/views/__init__.py`
- `periodic_table/views/search_bar.py` — `SearchBar(tk.Frame)`
- `periodic_table/views/grid_view.py` — `PeriodicGridView(tk.Frame)`
- `periodic_table/views/detail_window.py` — `ElementDetailWindow(tk.Toplevel)`
- `periodic_table/views/atom_view.py` — `AtomWindow(tk.Toplevel)`
- `tests/__init__.py`
- `tests/test_model.py`
- `tests/test_shells.py`
- `tests/test_placement.py`
- `tests/test_search.py`
- `tests/test_data.py`
- `tests/test_smoke_gui.py`
- `pyproject.toml`
- `.gitignore`
- `README.md`

**Modify:**
- `main.py` — replace stub with wiring code.

Each file has one responsibility. Pure logic separated from Tk widgets so unit tests don't need a display.

---

## Chunk 1: Scaffold and Pure Logic

### Task 1: Project scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `periodic_table/__init__.py`
- Create: `periodic_table/views/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1.1: Create `.gitignore`**

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.idea/
*.egg-info/
```

- [ ] **Step 1.2: Create `pyproject.toml`**

```toml
[project]
name = "periodic-table"
version = "0.1.0"
description = "Tkinter periodic table viewer."
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=7.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 1.3: Create empty package marker files**

```python
# periodic_table/__init__.py
# periodic_table/views/__init__.py
# tests/__init__.py
```

(All three files are empty.)

- [ ] **Step 1.4: Install pytest in the venv**

Precondition: `.venv/` exists. If not, run `python3 -m venv .venv` first.

Run: `.venv/bin/pip install -e ".[dev]"`
Expected: `Successfully installed periodic-table-0.1.0 pytest-...`

- [ ] **Step 1.5: Verify pytest discovers no tests yet**

Run: `.venv/bin/pytest -q`
Expected: `no tests ran`

- [ ] **Step 1.6: Commit**

```bash
git add .gitignore pyproject.toml periodic_table/__init__.py periodic_table/views/__init__.py tests/__init__.py
git commit -m "chore: scaffold periodic_table package and pytest config"
```

---

### Task 2: `model.Element` and `model.Category`

**Files:**
- Create: `periodic_table/model.py`
- Test: `tests/test_model.py`

- [ ] **Step 2.1: Write failing test**

`tests/test_model.py`:

```python
from periodic_table.model import Element, Category


def test_element_is_frozen_dataclass():
    e = Element(
        atomic_number=1,
        symbol="H",
        name="Hydrogen",
        mass=1.008,
        period=1,
        group=1,
        category=Category.NONMETAL,
        electron_config="1s1",
        electronegativity=2.20,
        phase="gas",
    )
    assert e.symbol == "H"
    assert e.atomic_number == 1
    try:
        e.symbol = "X"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("Element should be frozen")


def test_category_enum_has_required_members():
    expected = {
        "ALKALI_METAL", "ALKALINE_EARTH", "TRANSITION_METAL",
        "POST_TRANSITION", "METALLOID", "NONMETAL", "HALOGEN",
        "NOBLE_GAS", "LANTHANIDE", "ACTINIDE", "UNKNOWN",
    }
    assert {c.name for c in Category} == expected
```

- [ ] **Step 2.2: Run test, verify failure**

Run: `.venv/bin/pytest tests/test_model.py -v`
Expected: `ModuleNotFoundError: No module named 'periodic_table.model'`

- [ ] **Step 2.3: Implement `periodic_table/model.py`**

```python
from dataclasses import dataclass
from enum import Enum


class Category(Enum):
    ALKALI_METAL = "alkali metal"
    ALKALINE_EARTH = "alkaline earth"
    TRANSITION_METAL = "transition metal"
    POST_TRANSITION = "post-transition metal"
    METALLOID = "metalloid"
    NONMETAL = "nonmetal"
    HALOGEN = "halogen"
    NOBLE_GAS = "noble gas"
    LANTHANIDE = "lanthanide"
    ACTINIDE = "actinide"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Element:
    atomic_number: int
    symbol: str
    name: str
    mass: float
    period: int
    group: int | None
    category: Category
    electron_config: str
    electronegativity: float | None
    phase: str
```

- [ ] **Step 2.4: Run test, verify pass**

Run: `.venv/bin/pytest tests/test_model.py -v`
Expected: 2 passed

- [ ] **Step 2.5: Commit**

```bash
git add periodic_table/model.py tests/test_model.py
git commit -m "feat(model): add Element dataclass and Category enum"
```

---

### Task 3: `shells.fill_shells`

**Files:**
- Create: `periodic_table/shells.py`
- Test: `tests/test_shells.py`

- [ ] **Step 3.1: Write failing tests**

`tests/test_shells.py`:

```python
import pytest

from periodic_table.shells import fill_shells


@pytest.mark.parametrize("z, expected", [
    (1, [1]),
    (2, [2]),
    (3, [2, 1]),
    (10, [2, 8]),
    (11, [2, 8, 1]),
    (18, [2, 8, 8]),
    (54, [2, 8, 18, 18, 8]),
    (118, [2, 8, 18, 32, 32, 18, 8]),
])
def test_fill_shells_known_values(z, expected):
    assert fill_shells(z) == expected


def test_fill_shells_sum_equals_z_for_all_supported():
    for z in range(1, 119):
        assert sum(fill_shells(z)) == z
```

- [ ] **Step 3.2: Run tests, verify failure**

Run: `.venv/bin/pytest tests/test_shells.py -v`
Expected: `ModuleNotFoundError: No module named 'periodic_table.shells'`

- [ ] **Step 3.3: Implement `periodic_table/shells.py`**

```python
_CAPACITIES = (2, 8, 18, 32, 32, 18, 8)


def fill_shells(z: int) -> list[int]:
    if z < 1:
        raise ValueError("atomic number must be >= 1")
    remaining = z
    result: list[int] = []
    for cap in _CAPACITIES:
        if remaining == 0:
            break
        n = min(cap, remaining)
        result.append(n)
        remaining -= n
    if remaining > 0:
        raise ValueError(f"atomic number {z} exceeds supported shell capacity")
    return result
```

- [ ] **Step 3.4: Run tests, verify pass**

Run: `.venv/bin/pytest tests/test_shells.py -v`
Expected: all passed

- [ ] **Step 3.5: Commit**

```bash
git add periodic_table/shells.py tests/test_shells.py
git commit -m "feat(shells): add fill_shells Bohr electron-distribution function"
```

---

### Task 4: `placement.placement_for`

**Files:**
- Create: `periodic_table/placement.py`
- Test: `tests/test_placement.py`

Placement convention from spec:
- Rows 0..6 = periods 1..7 (main grid, cols 0..17 = groups 1..18).
- Row 7 = lanthanide strip (La..Lu) at cols 0..14.
- Row 8 = actinide strip (Ac..Lr) at cols 0..14.
- Placeholder markers at `(5, 2)` and `(6, 2)`.

- [ ] **Step 4.1: Write failing tests**

`tests/test_placement.py`:

```python
import pytest

from periodic_table.model import Category, Element
from periodic_table.placement import (
    LANTHANIDE_PLACEHOLDER,
    ACTINIDE_PLACEHOLDER,
    placement_for,
)


def make(z, period, group, category):
    return Element(
        atomic_number=z, symbol="X", name="X", mass=0.0,
        period=period, group=group, category=category,
        electron_config="", electronegativity=None, phase="unknown",
    )


@pytest.mark.parametrize("z, period, group, expected_row, expected_col", [
    (1, 1, 1, 0, 0),     # H
    (2, 1, 18, 0, 17),   # He
    (6, 2, 14, 1, 13),   # C
    (11, 3, 1, 2, 0),    # Na
    (118, 7, 18, 6, 17), # Og
])
def test_main_grid_placement(z, period, group, expected_row, expected_col):
    e = make(z, period, group, Category.NONMETAL)
    assert placement_for(e) == (expected_row, expected_col)


def test_lanthanum_placement():
    e = make(57, 6, None, Category.LANTHANIDE)
    assert placement_for(e) == (7, 0)


def test_lutetium_placement():
    e = make(71, 6, None, Category.LANTHANIDE)
    assert placement_for(e) == (7, 14)


def test_actinium_placement():
    e = make(89, 7, None, Category.ACTINIDE)
    assert placement_for(e) == (8, 0)


def test_lawrencium_placement():
    e = make(103, 7, None, Category.ACTINIDE)
    assert placement_for(e) == (8, 14)


def test_placeholder_constants():
    assert LANTHANIDE_PLACEHOLDER == (5, 2)
    assert ACTINIDE_PLACEHOLDER == (6, 2)
```

- [ ] **Step 4.2: Run tests, verify failure**

Run: `.venv/bin/pytest tests/test_placement.py -v`
Expected: `ModuleNotFoundError: No module named 'periodic_table.placement'`

- [ ] **Step 4.3: Implement `periodic_table/placement.py`**

```python
from periodic_table.model import Category, Element

LANTHANIDE_PLACEHOLDER: tuple[int, int] = (5, 2)
ACTINIDE_PLACEHOLDER: tuple[int, int] = (6, 2)

_LANTHANIDE_FIRST_Z = 57   # La
_ACTINIDE_FIRST_Z = 89     # Ac


def placement_for(element: Element) -> tuple[int, int]:
    if element.category is Category.LANTHANIDE:
        col = element.atomic_number - _LANTHANIDE_FIRST_Z
        if not 0 <= col <= 14:
            raise ValueError(f"lanthanide Z={element.atomic_number} out of range")
        return (7, col)

    if element.category is Category.ACTINIDE:
        col = element.atomic_number - _ACTINIDE_FIRST_Z
        if not 0 <= col <= 14:
            raise ValueError(f"actinide Z={element.atomic_number} out of range")
        return (8, col)

    if element.group is None:
        raise ValueError(
            f"non-La/Ac element {element.symbol} (Z={element.atomic_number}) has no group"
        )
    if not 1 <= element.period <= 7:
        raise ValueError(f"unsupported period {element.period}")
    if not 1 <= element.group <= 18:
        raise ValueError(f"invalid group {element.group}")
    return (element.period - 1, element.group - 1)
```

- [ ] **Step 4.4: Run tests, verify pass**

Run: `.venv/bin/pytest tests/test_placement.py -v`
Expected: all passed

- [ ] **Step 4.5: Commit**

```bash
git add periodic_table/placement.py tests/test_placement.py
git commit -m "feat(placement): add placement_for and La/Ac placeholder constants"
```

---

### Task 5: `search.match`

**Files:**
- Create: `periodic_table/search.py`
- Test: `tests/test_search.py`

- [ ] **Step 5.1: Write failing tests**

`tests/test_search.py`:

```python
import pytest

from periodic_table.model import Category, Element
from periodic_table.search import match


SODIUM = Element(
    atomic_number=11, symbol="Na", name="Sodium", mass=22.99,
    period=3, group=1, category=Category.ALKALI_METAL,
    electron_config="[Ne] 3s1", electronegativity=0.93, phase="solid",
)


@pytest.mark.parametrize("query", ["", "   "])
def test_empty_query_matches(query):
    assert match(query, SODIUM) is True


def test_symbol_exact_match_case_insensitive():
    assert match("Na", SODIUM) is True
    assert match("na", SODIUM) is True
    assert match("NA", SODIUM) is True


def test_symbol_prefix_does_not_match():
    assert match("N", SODIUM) is False  # would match Nitrogen, not Sodium


def test_name_prefix_match_case_insensitive():
    assert match("sod", SODIUM) is True
    assert match("Sodi", SODIUM) is True


def test_atomic_number_match():
    assert match("11", SODIUM) is True
    assert match("12", SODIUM) is False


def test_no_match():
    assert match("xyz", SODIUM) is False
```

- [ ] **Step 5.2: Run tests, verify failure**

Run: `.venv/bin/pytest tests/test_search.py -v`
Expected: `ModuleNotFoundError: No module named 'periodic_table.search'`

- [ ] **Step 5.3: Implement `periodic_table/search.py`**

```python
from periodic_table.model import Element


def match(query: str, element: Element) -> bool:
    q = query.strip()
    if not q:
        return True
    q_lower = q.lower()
    if element.symbol.lower() == q_lower:
        return True
    if element.name.lower().startswith(q_lower):
        return True
    try:
        if int(q) == element.atomic_number:
            return True
    except ValueError:
        pass
    return False
```

- [ ] **Step 5.4: Run tests, verify pass**

Run: `.venv/bin/pytest tests/test_search.py -v`
Expected: all passed

- [ ] **Step 5.5: Commit**

```bash
git add periodic_table/search.py tests/test_search.py
git commit -m "feat(search): add match() for symbol/name/Z filtering"
```

---

## Chunk 2: Static Dataset and Category Colors

### Task 6: `categories.CATEGORY_COLORS`

**Files:**
- Create: `periodic_table/categories.py`
- Test: `tests/test_categories.py`

- [ ] **Step 6.1: Write failing test**

`tests/test_categories.py`:

```python
from periodic_table.categories import CATEGORY_COLORS, DIM_COLOR
from periodic_table.model import Category


def test_every_category_has_a_color():
    missing = [c for c in Category if c not in CATEGORY_COLORS]
    assert not missing, missing


def test_colors_are_hex_strings():
    for c, color in CATEGORY_COLORS.items():
        assert isinstance(color, str), c
        assert color.startswith("#") and len(color) == 7, (c, color)


def test_dim_color_is_distinct():
    assert DIM_COLOR not in CATEGORY_COLORS.values()
```

- [ ] **Step 6.2: Run test, verify failure**

Run: `.venv/bin/pytest tests/test_categories.py -v`
Expected: `ModuleNotFoundError: No module named 'periodic_table.categories'`

- [ ] **Step 6.3: Implement `periodic_table/categories.py`**

```python
from periodic_table.model import Category

CATEGORY_COLORS: dict[Category, str] = {
    Category.ALKALI_METAL:      "#ff6666",
    Category.ALKALINE_EARTH:    "#ffdead",
    Category.TRANSITION_METAL:  "#ffc0c0",
    Category.POST_TRANSITION:   "#bfbfbf",
    Category.METALLOID:         "#cccc99",
    Category.NONMETAL:          "#a0ffa0",
    Category.HALOGEN:           "#ffff99",
    Category.NOBLE_GAS:         "#c0ffff",
    Category.LANTHANIDE:        "#ffbfff",
    Category.ACTINIDE:          "#ff99cc",
    Category.UNKNOWN:           "#e0e0e0",
}

DIM_COLOR = "#dddddd"
```

- [ ] **Step 6.4: Run test, verify pass**

Run: `.venv/bin/pytest tests/test_categories.py -v`
Expected: 3 passed

- [ ] **Step 6.5: Commit**

```bash
git add periodic_table/categories.py tests/test_categories.py
git commit -m "feat(categories): add CATEGORY_COLORS palette"
```

---

### Task 7: `data.ELEMENTS` — invariants test first

**Files:**
- Create: `tests/test_data.py`
- Create: `periodic_table/data.py`

Write invariants AND spot-check tests BEFORE the dataset so the dataset is built against a concrete contract. Spot-checks catch hand-typed dataset errors that structural invariants cannot.

#### Reference source (LOCKED)

The executor MUST use a single authoritative source for the dataset. Cite this commit's choice and stick to it:

- **Source:** Wikipedia "List of chemical elements" — table columns Z, symbol, name, standard atomic weight, group, period, electron configuration (Madelung order), electronegativity (Pauling), standard state (phase).
- **Snapshot date:** 2026-06-03.
- If a value is debated in the source (multi-row footnoted), pick the canonical IUPAC value listed first.

#### Category assignments (LOCKED)

Use this exact mapping; do not improvise. This removes the spec's "post-transition vs metalloid borderline" ambiguity and the superheavy "UNKNOWN" gray zone.

| Category | Members (by symbol) |
|----------|---------------------|
| `NONMETAL` | H, C, N, O, P, S, Se |
| `NOBLE_GAS` | He, Ne, Ar, Kr, Xe, Rn, Og |
| `ALKALI_METAL` | Li, Na, K, Rb, Cs, Fr |
| `ALKALINE_EARTH` | Be, Mg, Ca, Sr, Ba, Ra |
| `METALLOID` | B, Si, Ge, As, Sb, Te |
| `HALOGEN` | F, Cl, Br, I, At, Ts |
| `POST_TRANSITION` | Al, Ga, In, Sn, Tl, Pb, Bi, Po, Nh, Fl, Mc, Lv |
| `LANTHANIDE` | La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu (Z 57–71) |
| `ACTINIDE` | Ac, Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf, Es, Fm, Md, No, Lr (Z 89–103) |
| `TRANSITION_METAL` | Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Rf, Db, Sg, Bh, Hs, Mt, Ds, Rg, Cn |
| `UNKNOWN` | (none in this dataset; enum member retained for future use) |

#### Group / period notes (LOCKED)

- H: `group=1`, `period=1`.
- He: `group=18`, `period=1`.
- Lanthanides (Z 57–71): `group=None`, `period=6`.
- Actinides (Z 89–103): `group=None`, `period=7`.
- Superheavies Rf (104) → Cn (112): `period=7`, groups 4–12 in order.
- Nh (113) → Og (118): `period=7`, groups 13–18 in order.

#### Phase set (LOCKED)

Only `"solid"`, `"liquid"`, `"gas"`, `"unknown"` are valid. At STP:
- `"liquid"` for Br and Hg only.
- `"gas"` for H, He, N, O, F, Ne, Cl, Ar, Kr, Xe, Rn.
- `"unknown"` for synthetic superheavies with no measured bulk phase: Rf onwards (Z ≥ 104). Use `"unknown"` for Z 104–118.
- All other measured elements: `"solid"`.

- [ ] **Step 7.1: Write failing tests (invariants + spot-checks + collision)**

`tests/test_data.py`:

```python
import pytest

from periodic_table.data import ELEMENTS
from periodic_table.model import Category
from periodic_table.placement import placement_for


# ---- Structural invariants ------------------------------------------------

def test_count_is_118():
    assert len(ELEMENTS) == 118


def test_atomic_numbers_are_contiguous_1_to_118():
    zs = sorted(e.atomic_number for e in ELEMENTS)
    assert zs == list(range(1, 119))


def test_symbols_unique():
    syms = [e.symbol for e in ELEMENTS]
    assert len(set(syms)) == 118


def test_names_unique():
    names = [e.name for e in ELEMENTS]
    assert len(set(names)) == 118


def test_periods_in_range():
    for e in ELEMENTS:
        assert 1 <= e.period <= 7, (e.symbol, e.period)


def test_group_rules():
    for e in ELEMENTS:
        if e.category in (Category.LANTHANIDE, Category.ACTINIDE):
            assert e.group is None, (e.symbol, e.group)
        else:
            assert e.group is not None and 1 <= e.group <= 18, (e.symbol, e.group)


def test_every_element_has_a_grid_placement():
    for e in ELEMENTS:
        row, col = placement_for(e)
        assert 0 <= row <= 8
        assert 0 <= col <= 17


def test_no_two_elements_collide_in_grid():
    seen: dict[tuple[int, int], str] = {}
    for e in ELEMENTS:
        pos = placement_for(e)
        assert pos not in seen, (pos, seen[pos], e.symbol)
        seen[pos] = e.symbol


def test_phase_values_are_valid():
    valid = {"solid", "liquid", "gas", "unknown"}
    for e in ELEMENTS:
        assert e.phase in valid, (e.symbol, e.phase)


def test_electronegativity_is_float_or_none():
    for e in ELEMENTS:
        assert e.electronegativity is None or isinstance(e.electronegativity, float)


# ---- Spot-checks (catch typos in reference values) ------------------------

def by_z(z: int):
    return next(e for e in ELEMENTS if e.atomic_number == z)


def test_hydrogen_basics():
    h = by_z(1)
    assert h.symbol == "H"
    assert h.name == "Hydrogen"
    assert h.group == 1
    assert h.period == 1
    assert h.phase == "gas"
    assert h.category is Category.NONMETAL
    assert h.electronegativity == pytest.approx(2.20, rel=0.02)


def test_helium_basics():
    he = by_z(2)
    assert he.symbol == "He"
    assert he.group == 18
    assert he.period == 1
    assert he.category is Category.NOBLE_GAS
    assert he.electronegativity is None
    assert he.phase == "gas"


def test_iron_basics():
    fe = by_z(26)
    assert fe.symbol == "Fe"
    assert fe.category is Category.TRANSITION_METAL
    assert fe.mass == pytest.approx(55.845, rel=0.001)


def test_bromine_is_liquid_halogen():
    br = by_z(35)
    assert br.symbol == "Br"
    assert br.phase == "liquid"
    assert br.category is Category.HALOGEN


def test_caesium_electronegativity():
    cs = by_z(55)
    assert cs.symbol == "Cs"
    assert cs.electronegativity == pytest.approx(0.79, rel=0.02)


def test_lanthanum_is_lanthanide_no_group():
    la = by_z(57)
    assert la.category is Category.LANTHANIDE
    assert la.group is None
    assert la.period == 6


def test_gold_basics():
    au = by_z(79)
    assert au.symbol == "Au"
    assert au.category is Category.TRANSITION_METAL
    assert au.electronegativity == pytest.approx(2.54, rel=0.02)
    assert au.phase == "solid"


def test_mercury_is_liquid_transition_metal():
    hg = by_z(80)
    assert hg.symbol == "Hg"
    assert hg.phase == "liquid"
    assert hg.category is Category.TRANSITION_METAL


def test_lawrencium_is_actinide():
    lr = by_z(103)
    assert lr.symbol == "Lr"
    assert lr.category is Category.ACTINIDE
    assert lr.group is None
    assert lr.period == 7


def test_oganesson_basics():
    og = by_z(118)
    assert og.symbol == "Og"
    assert og.period == 7
    assert og.group == 18
    assert og.category is Category.NOBLE_GAS
    assert og.phase == "unknown"
```

- [ ] **Step 7.2: Run tests, verify failure**

Run: `.venv/bin/pytest tests/test_data.py -v`
Expected: `ModuleNotFoundError: No module named 'periodic_table.data'`

- [ ] **Step 7.3: Implement `periodic_table/data.py`**

Create a module with a single list `ELEMENTS: list[Element]` of length 118. For every Z in 1..118, instantiate one `Element` populated from the LOCKED reference source above. The skeleton:

```python
from periodic_table.model import Category, Element

ELEMENTS: list[Element] = [
    Element(atomic_number=1,  symbol="H",  name="Hydrogen", mass=1.008,
            period=1, group=1,  category=Category.NONMETAL,
            electron_config="1s1",
            electronegativity=2.20, phase="gas"),
    Element(atomic_number=2,  symbol="He", name="Helium",   mass=4.0026,
            period=1, group=18, category=Category.NOBLE_GAS,
            electron_config="1s2",
            electronegativity=None, phase="gas"),
    Element(atomic_number=3,  symbol="Li", name="Lithium",  mass=6.94,
            period=2, group=1,  category=Category.ALKALI_METAL,
            electron_config="[He] 2s1",
            electronegativity=0.98, phase="solid"),
    # ... one Element(...) literal per Z from 4 through 118.
]
```

Rules the executor MUST follow while filling rows:

1. Order the list strictly by ascending atomic number (Z 1 → 118). No sorting at runtime.
2. Pull `symbol`, `name`, `mass`, `period`, `group`, `electron_config`, `electronegativity`, `phase` from the LOCKED Wikipedia source listed above.
3. Use `None` for electronegativity if the source lists "—" or "no data" (typical for noble gases and some superheavies).
4. Set `category` from the LOCKED category table — do not infer from group/period.
5. Set `group=None` for every lanthanide (57–71) and actinide (89–103). Set `group` per the LOCKED Group/period notes for all others.
6. Set `phase` per the LOCKED Phase set rules above.

The file will be ~118 lines of `Element(...)` constructors plus the import. That is its single responsibility — flat data — and is acceptable as one file.

- [ ] **Step 7.4: Run tests, verify pass**

Run: `.venv/bin/pytest tests/test_data.py -v`
Expected: all 19 tests passed.

- [ ] **Step 7.5: Commit**

```bash
git add periodic_table/data.py tests/test_data.py
git commit -m "feat(data): add static dataset of 118 elements with spot-check tests"
```

---

## Chunk 3: Tk Views and Wiring

### Task 8: `views.search_bar.SearchBar`

**Files:**
- Create: `periodic_table/views/search_bar.py`

GUI widget — no unit test; exercised via smoke test (Task 13).

- [ ] **Step 8.1: Implement `periodic_table/views/search_bar.py`**

```python
import tkinter as tk
from typing import Callable


class SearchBar(tk.Frame):
    def __init__(self, parent: tk.Misc, on_change: Callable[[str], None]) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self._var = tk.StringVar()
        self._var.trace_add("write", self._handle_write)

        tk.Label(self, text="Search:").pack(side=tk.LEFT, padx=(4, 4))
        tk.Entry(self, textvariable=self._var, width=40).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4,
        )

    def _handle_write(self, *_: object) -> None:
        self._on_change(self._var.get())
```

- [ ] **Step 8.2: Quick import check**

Run: `.venv/bin/python -c "from periodic_table.views.search_bar import SearchBar; print(SearchBar)"`
Expected: prints `<class 'periodic_table.views.search_bar.SearchBar'>`

- [ ] **Step 8.3: Commit**

```bash
git add periodic_table/views/search_bar.py
git commit -m "feat(views): add SearchBar widget"
```

---

### Task 9: `views.grid_view.PeriodicGridView`

**Files:**
- Create: `periodic_table/views/grid_view.py`

Responsibilities: build a button per element using `placement_for`, render La/Ac placeholders, and expose `highlight(query)` which dims non-matching cells.

- [ ] **Step 9.1: Implement `periodic_table/views/grid_view.py`**

```python
import tkinter as tk
from typing import Callable

from periodic_table.categories import CATEGORY_COLORS, DIM_COLOR
from periodic_table.data import ELEMENTS
from periodic_table.model import Element
from periodic_table.placement import (
    ACTINIDE_PLACEHOLDER,
    LANTHANIDE_PLACEHOLDER,
    placement_for,
)
from periodic_table.search import match


class PeriodicGridView(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        on_select: Callable[[Element], None],
    ) -> None:
        super().__init__(parent)
        self._on_select = on_select
        self._cells: dict[int, tuple[tk.Button, str]] = {}  # Z -> (button, base_color)

        for element in ELEMENTS:
            row, col = placement_for(element)
            base = CATEGORY_COLORS[element.category]
            btn = tk.Button(
                self,
                text=f"{element.atomic_number}\n{element.symbol}",
                bg=base,
                width=4,
                height=2,
                relief=tk.RAISED,
                command=lambda e=element: self._on_select(e),
            )
            btn.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            self._cells[element.atomic_number] = (btn, base)

        tk.Label(self, text="*",  bg="#ffffff").grid(
            row=LANTHANIDE_PLACEHOLDER[0], column=LANTHANIDE_PLACEHOLDER[1],
            padx=1, pady=1, sticky="nsew",
        )
        tk.Label(self, text="**", bg="#ffffff").grid(
            row=ACTINIDE_PLACEHOLDER[0], column=ACTINIDE_PLACEHOLDER[1],
            padx=1, pady=1, sticky="nsew",
        )

    def highlight(self, query: str) -> None:
        for element in ELEMENTS:
            btn, base = self._cells[element.atomic_number]
            btn.configure(bg=base if match(query, element) else DIM_COLOR)
```

- [ ] **Step 9.2: Quick import check**

Run: `.venv/bin/python -c "from periodic_table.views.grid_view import PeriodicGridView; print(PeriodicGridView)"`
Expected: prints the class.

- [ ] **Step 9.3: Commit**

```bash
git add periodic_table/views/grid_view.py
git commit -m "feat(views): add PeriodicGridView with highlight support"
```

---

### Task 10: `views.atom_view.AtomWindow`

**Files:**
- Create: `periodic_table/views/atom_view.py`

- [ ] **Step 10.1: Implement `periodic_table/views/atom_view.py`**

```python
import math
import tkinter as tk

from periodic_table.model import Element
from periodic_table.shells import fill_shells

_CANVAS_SIZE = 600
_CENTER = _CANVAS_SIZE // 2
_NUCLEUS_R = 20
_INNER_OFFSET = 30
_OUTER_MAX = 250
_ELECTRON_R = 4


class AtomWindow(tk.Toplevel):
    def __init__(self, parent: tk.Misc, element: Element) -> None:
        super().__init__(parent)
        self.title(f"Atom — {element.name}")
        self.transient(parent)

        canvas = tk.Canvas(
            self, width=_CANVAS_SIZE, height=_CANVAS_SIZE, bg="white", highlightthickness=0,
        )
        canvas.pack(padx=8, pady=8)
        self._draw(canvas, element)

    @staticmethod
    def _draw(canvas: tk.Canvas, element: Element) -> None:
        canvas.create_oval(
            _CENTER - _NUCLEUS_R, _CENTER - _NUCLEUS_R,
            _CENTER + _NUCLEUS_R, _CENTER + _NUCLEUS_R,
            fill="#444", outline="",
        )
        canvas.create_text(
            _CENTER, _CENTER,
            text=f"{element.symbol}\n{element.atomic_number}",
            fill="white", justify=tk.CENTER, font=("TkDefaultFont", 10, "bold"),
        )

        shells = fill_shells(element.atomic_number)
        k = len(shells)
        step = _OUTER_MAX // k

        for i, count in enumerate(shells, start=1):
            r = _INNER_OFFSET + i * step
            canvas.create_oval(
                _CENTER - r, _CENTER - r,
                _CENTER + r, _CENTER + r,
                outline="#888",
            )
            for n in range(count):
                theta = 2 * math.pi * n / count
                x = _CENTER + r * math.cos(theta)
                y = _CENTER + r * math.sin(theta)
                canvas.create_oval(
                    x - _ELECTRON_R, y - _ELECTRON_R,
                    x + _ELECTRON_R, y + _ELECTRON_R,
                    fill="#1f77b4", outline="",
                )
```

- [ ] **Step 10.2: Quick import check**

Run: `.venv/bin/python -c "from periodic_table.views.atom_view import AtomWindow; print(AtomWindow)"`
Expected: prints the class.

- [ ] **Step 10.3: Commit**

```bash
git add periodic_table/views/atom_view.py
git commit -m "feat(views): add AtomWindow Bohr-model renderer"
```

---

### Task 11: `views.detail_window.ElementDetailWindow`

**Files:**
- Create: `periodic_table/views/detail_window.py`

- [ ] **Step 11.1: Implement `periodic_table/views/detail_window.py`**

```python
import tkinter as tk

from periodic_table.model import Element
from periodic_table.views.atom_view import AtomWindow


def _fmt(value: object) -> str:
    return "—" if value is None else str(value)


class ElementDetailWindow(tk.Toplevel):
    _FIELDS: tuple[tuple[str, str], ...] = (
        ("Name",                "name"),
        ("Symbol",              "symbol"),
        ("Atomic number",       "atomic_number"),
        ("Atomic mass",         "mass"),
        ("Period",              "period"),
        ("Group",               "group"),
        ("Category",            None),  # special-cased: enum.value
        ("Electron config",     "electron_config"),
        ("Electronegativity",   "electronegativity"),
        ("Phase",               "phase"),
    )

    def __init__(self, parent: tk.Misc, element: Element) -> None:
        super().__init__(parent)
        self.title(element.name)
        self.transient(parent)

        body = tk.Frame(self, padx=12, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        for row, (label, attr) in enumerate(self._FIELDS):
            tk.Label(body, text=f"{label}:", anchor="e", width=20).grid(
                row=row, column=0, sticky="e", padx=(0, 8), pady=2,
            )
            if attr is None:
                value: object = element.category.value
            else:
                value = getattr(element, attr)
            tk.Label(body, text=_fmt(value), anchor="w").grid(
                row=row, column=1, sticky="w", pady=2,
            )

        tk.Button(
            body, text="Show atom",
            command=lambda: AtomWindow(self, element),
        ).grid(row=len(self._FIELDS), column=0, columnspan=2, pady=(12, 0))
```

- [ ] **Step 11.2: Quick import check**

Run: `.venv/bin/python -c "from periodic_table.views.detail_window import ElementDetailWindow; print(ElementDetailWindow)"`
Expected: prints the class.

- [ ] **Step 11.3: Commit**

```bash
git add periodic_table/views/detail_window.py
git commit -m "feat(views): add ElementDetailWindow with Show atom button"
```

---

### Task 12: `main.py` wiring

**Files:**
- Modify: `main.py`

- [ ] **Step 12.1: Replace `main.py` contents**

```python
import tkinter as tk

from periodic_table.model import Element
from periodic_table.views.detail_window import ElementDetailWindow
from periodic_table.views.grid_view import PeriodicGridView
from periodic_table.views.search_bar import SearchBar


def main() -> None:
    root = tk.Tk()
    root.title("Periodic Table of Elements")

    grid_view = PeriodicGridView(
        root,
        on_select=lambda e: _open_detail(root, e),
    )
    search_bar = SearchBar(root, on_change=grid_view.highlight)

    search_bar.pack(fill=tk.X)
    grid_view.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    root.mainloop()


def _open_detail(parent: tk.Misc, element: Element) -> None:
    ElementDetailWindow(parent, element)


if __name__ == "__main__":
    main()
```

- [ ] **Step 12.2: Manual smoke run**

Run: `.venv/bin/python main.py`
Expected: Tk window opens showing the periodic table grid; search bar at top; clicking an element opens a detail popup; clicking "Show atom" opens an atom-diagram window.

Close the window when verified.

- [ ] **Step 12.3: Commit**

```bash
git add main.py
git commit -m "feat: wire SearchBar, PeriodicGridView, and ElementDetailWindow in main"
```

---

### Task 13: Smoke test

**Files:**
- Create: `tests/test_smoke_gui.py`

- [ ] **Step 13.1: Write smoke test**

```python
import pytest

tk = pytest.importorskip("tkinter")

from periodic_table.data import ELEMENTS  # noqa: E402
from periodic_table.views.atom_view import AtomWindow  # noqa: E402
from periodic_table.views.detail_window import ElementDetailWindow  # noqa: E402
from periodic_table.views.grid_view import PeriodicGridView  # noqa: E402
from periodic_table.views.search_bar import SearchBar  # noqa: E402


@pytest.fixture
def root():
    try:
        r = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk display unavailable: {exc}")
    r.withdraw()
    yield r
    r.destroy()


def test_smoke_construct_all_widgets(root):
    grid = PeriodicGridView(root, on_select=lambda _e: None)
    bar = SearchBar(root, on_change=grid.highlight)
    detail = ElementDetailWindow(root, ELEMENTS[0])   # Hydrogen
    atom = AtomWindow(root, ELEMENTS[-1])             # Oganesson
    grid.highlight("Na")
    grid.highlight("")
    assert bar is not None
    assert detail is not None
    assert atom is not None
```

- [ ] **Step 13.2: Run smoke test**

Run: `.venv/bin/pytest tests/test_smoke_gui.py -v`
Expected on a desktop with Tk: passed. On headless CI without Tk: skipped.

- [ ] **Step 13.3: Run the full test suite**

Run: `.venv/bin/pytest -v`
Expected: all tests pass (or smoke test skipped on headless env). No failures.

- [ ] **Step 13.4: Commit**

```bash
git add tests/test_smoke_gui.py
git commit -m "test: add smoke test for all Tk widgets"
```

---

### Task 14: README

**Files:**
- Create: `README.md`

- [ ] **Step 14.1: Write `README.md`**

```markdown
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
```

- [ ] **Step 14.2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup and run instructions"
```

---

## Done Criteria

- `.venv/bin/pytest -v` shows all non-GUI tests passing and the GUI smoke test passing (or cleanly skipped on headless environments).
- `.venv/bin/python main.py` opens the periodic table window; clicking an element opens a detail popup; the popup's "Show atom" button opens an atom diagram window.
- Git history contains one commit per task with conventional-commit subjects.
