import pytest

from periodic_table.shells import fill_shells


@pytest.mark.parametrize("z, expected", [
    (1, [1]),
    (2, [2]),
    (3, [2, 1]),
    (10, [2, 8]),
    (11, [2, 8, 1]),
    (18, [2, 8, 8]),
    (54, [2, 8, 18, 26]),
    (118, [2, 8, 18, 32, 32, 18, 8]),
])
def test_fill_shells_known_values(z, expected):
    assert fill_shells(z) == expected


def test_fill_shells_sum_equals_z_for_all_supported():
    for z in range(1, 119):
        assert sum(fill_shells(z)) == z
