import tkinter as tk
from typing import Callable

from periodic_table.categories import CATEGORY_COLORS, DIM_COLOR
from periodic_table.data import ELEMENTS
from periodic_table.model import Element
from periodic_table.placement import (
    ACTINIDE_PLACEHOLDER,
    LANTHANIDE_PLACEHOLDER,
    placement_for,
)
from periodic_table.search import match


class PeriodicGridView(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        on_select: Callable[[Element], None],
    ) -> None:
        super().__init__(parent)
        self._on_select = on_select
        self._cells: dict[int, tuple[tk.Label, str]] = {}  # Z -> (cell, base_color)

        for element in ELEMENTS:
            row, col = placement_for(element)
            base = CATEGORY_COLORS[element.category]
            cell = tk.Label(
                self,
                text=f"{element.atomic_number}\n{element.symbol}",
                bg=base,
                fg="black",
                width=4,
                height=2,
                relief=tk.RAISED,
                borderwidth=1,
                cursor="hand2",
            )
            cell.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            cell.bind("<Button-1>", lambda _ev, e=element: self._on_select(e))
            self._cells[element.atomic_number] = (cell, base)

        tk.Label(self, text="*",  bg="#ffffff").grid(
            row=LANTHANIDE_PLACEHOLDER[0], column=LANTHANIDE_PLACEHOLDER[1],
            padx=1, pady=1, sticky="nsew",
        )
        tk.Label(self, text="**", bg="#ffffff").grid(
            row=ACTINIDE_PLACEHOLDER[0], column=ACTINIDE_PLACEHOLDER[1],
            padx=1, pady=1, sticky="nsew",
        )

        tk.Label(
            self,
            text="Periodic Table of Elements",
            font=("TkDefaultFont", 20, "bold"),
        ).grid(row=0, column=2, columnspan=15, sticky="nsew", padx=4, pady=4)

    def highlight(self, query: str) -> None:
        for element in ELEMENTS:
            cell, base = self._cells[element.atomic_number]
            cell.configure(bg=base if match(query, element) else DIM_COLOR)
