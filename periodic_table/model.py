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