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