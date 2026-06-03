import tkinter as tk
from typing import Callable


class SearchBar(tk.Frame):
    def __init__(self, parent: tk.Misc, on_change: Callable[[str], None]) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self._var = tk.StringVar()
        self._var.trace_add("write", self._handle_write)

        tk.Label(self, text="Search:").pack(side=tk.LEFT, padx=(4, 4))
        tk.Entry(self, textvariable=self._var, width=40).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4,
        )

    def _handle_write(self, *_: object) -> None:
        self._on_change(self._var.get())
