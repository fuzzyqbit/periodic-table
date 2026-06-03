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
