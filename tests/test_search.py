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