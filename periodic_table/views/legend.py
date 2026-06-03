import tkinter as tk

from periodic_table.categories import CATEGORY_COLORS
from periodic_table.model import Category


_DISPLAY_ORDER: tuple[Category, ...] = (
    Category.ALKALI_METAL,
    Category.ALKALINE_EARTH,
    Category.TRANSITION_METAL,
    Category.POST_TRANSITION,
    Category.METALLOID,
    Category.NONMETAL,
    Category.HALOGEN,
    Category.NOBLE_GAS,
    Category.LANTHANIDE,
    Category.ACTINIDE,
    Category.UNKNOWN,
)


class CategoryLegend(tk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        for col, category in enumerate(_DISPLAY_ORDER):
            cell = tk.Frame(self, padx=4, pady=2)
            cell.grid(row=0, column=col, padx=4, pady=4)
            tk.Label(
                cell, text="  ", bg=CATEGORY_COLORS[category],
                relief=tk.SOLID, borderwidth=1, width=3,
            ).pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(cell, text=category.value).pack(side=tk.LEFT)
