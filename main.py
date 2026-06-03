#!/usr/bin/env python3
import tkinter as tk

from periodic_table.model import Element
from periodic_table.views.detail_window import ElementDetailWindow
from periodic_table.views.grid_view import PeriodicGridView
from periodic_table.views.legend import CategoryLegend
from periodic_table.views.search_bar import SearchBar


def main() -> None:
    root = tk.Tk()
    root.title("Periodic Table of Elements")

    grid_view = PeriodicGridView(
        root,
        on_select=lambda e: _open_detail(root, e),
    )
    search_bar = SearchBar(root, on_change=grid_view.highlight)

    legend = CategoryLegend(root)

    search_bar.pack(fill=tk.X)
    grid_view.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
    legend.pack(fill=tk.X, padx=4, pady=(0, 4))

    root.mainloop()


def _open_detail(parent: tk.Misc, element: Element) -> None:
    ElementDetailWindow(parent, element)


if __name__ == "__main__":
    main()
