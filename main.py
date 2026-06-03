#!/usr/bin/env python3
import tkinter as tk

from periodic_table.model import Element
from periodic_table.views.compare import ComparisonWindow
from periodic_table.views.detail_window import ElementDetailWindow
from periodic_table.views.grid_view import PeriodicGridView
from periodic_table.views.legend import CategoryLegend
from periodic_table.views.quiz import QuizWindow
from periodic_table.views.search_bar import SearchBar
from periodic_table.views.timeline import TimelineSlider


def main() -> None:
    root = tk.Tk()
    root.title("Periodic Table of Elements")
    root.geometry("1400x800")

    grid_view = PeriodicGridView(
        root,
        on_select=lambda e: _open_detail(root, e),
        on_compare=lambda a, b: ComparisonWindow(root, a, b),
    )
    search_bar = SearchBar(root, on_change=grid_view.highlight)
    timeline = TimelineSlider(root, on_year_change=grid_view.filter_by_year)
    legend = CategoryLegend(root)

    toolbar = tk.Frame(root)
    tk.Button(
        toolbar, text="Quiz",
        command=lambda: QuizWindow(
            root,
            attach_click_handler=grid_view.set_click_handler,
            detach_click_handler=grid_view.reset_click_handler,
            flash_cell=grid_view.flash_cell,
        ),
    ).pack(side=tk.LEFT, padx=(0, 8))
    tk.Label(
        toolbar,
        text="Shift+click two elements to compare them.",
        fg="#555",
    ).pack(side=tk.LEFT)

    search_bar.pack(fill=tk.X)
    toolbar.pack(fill=tk.X, padx=4, pady=(0, 4))
    timeline.pack(fill=tk.X, padx=4, pady=(0, 4))
    grid_view.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
    legend.pack(fill=tk.X, padx=4, pady=(0, 4))

    root.mainloop()


def _open_detail(parent: tk.Misc, element: Element) -> None:
    ElementDetailWindow(parent, element)


if __name__ == "__main__":
    main()
