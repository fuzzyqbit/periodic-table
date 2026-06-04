#!/usr/bin/env python3
"""Export the static element dataset to web/elements.json for the web app."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from periodic_table.categories import CATEGORY_COLORS, DIM_COLOR
from periodic_table.data import ELEMENTS
from periodic_table.discovery import DISCOVERED_YEAR
from periodic_table.placement import (
    ACTINIDE_PLACEHOLDER,
    LANTHANIDE_PLACEHOLDER,
    placement_for,
)


def main() -> None:
    elements = []
    for e in ELEMENTS:
        row, col = placement_for(e)
        elements.append({
            "z": e.atomic_number,
            "symbol": e.symbol,
            "name": e.name,
            "mass": e.mass,
            "period": e.period,
            "group": e.group,
            "category": e.category.name,
            "category_label": e.category.value,
            "electron_config": e.electron_config,
            "electronegativity": e.electronegativity,
            "phase": e.phase,
            "row": row,
            "col": col,
            "discovered": DISCOVERED_YEAR[e.atomic_number],
        })

    payload = {
        "elements": elements,
        "category_colors": {c.name: v for c, v in CATEGORY_COLORS.items()},
        "dim_color": DIM_COLOR,
        "lanthanide_placeholder": list(LANTHANIDE_PLACEHOLDER),
        "actinide_placeholder": list(ACTINIDE_PLACEHOLDER),
    }

    out = ROOT / "web" / "elements.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {len(elements)} elements to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
