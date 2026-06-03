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