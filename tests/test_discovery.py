from periodic_table.data import ELEMENTS
from periodic_table.discovery import DISCOVERED_YEAR


def test_every_element_has_a_year():
    for e in ELEMENTS:
        assert e.atomic_number in DISCOVERED_YEAR, e.symbol


def test_years_are_ints():
    for z, year in DISCOVERED_YEAR.items():
        assert isinstance(year, int), (z, year)


def test_no_year_after_2025():
    for z, year in DISCOVERED_YEAR.items():
        assert year <= 2025, (z, year)


def test_ancient_sentinel_is_zero():
    assert DISCOVERED_YEAR[1] != 0
    assert DISCOVERED_YEAR[79] == 0


def test_known_years_spot_check():
    assert DISCOVERED_YEAR[1] == 1766
    assert DISCOVERED_YEAR[8] == 1774
    assert DISCOVERED_YEAR[88] == 1898
    assert DISCOVERED_YEAR[94] == 1940
