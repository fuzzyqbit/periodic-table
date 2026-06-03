import tkinter as tk
from typing import Callable

MIN_YEAR = 1600
MAX_YEAR = 2025


class TimelineSlider(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        on_year_change: Callable[[int], None],
    ) -> None:
        super().__init__(parent)
        self._on_year_change = on_year_change

        tk.Label(self, text="Show elements known by:").pack(side=tk.LEFT, padx=(4, 8))

        self._scale = tk.Scale(
            self,
            from_=MIN_YEAR, to=MAX_YEAR,
            orient=tk.HORIZONTAL,
            length=600,
            command=self._handle_change,
            showvalue=False,
        )
        self._scale.set(MAX_YEAR)
        self._scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self._year_label = tk.Label(self, text=str(MAX_YEAR), width=6, font=("TkDefaultFont", 11, "bold"))
        self._year_label.pack(side=tk.LEFT, padx=(8, 4))

        tk.Button(self, text="Reset", command=self._reset).pack(side=tk.LEFT, padx=4)

    def _handle_change(self, value: str) -> None:
        year = int(float(value))
        self._year_label.configure(text=str(year))
        self._on_year_change(year)

    def _reset(self) -> None:
        self._scale.set(MAX_YEAR)