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