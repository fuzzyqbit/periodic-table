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
