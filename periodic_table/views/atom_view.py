import math
import tkinter as tk

from periodic_table.model import Element
from periodic_table.shells import fill_shells

_CANVAS_SIZE = 600
_CENTER = _CANVAS_SIZE // 2
_NUCLEUS_R = 20
_INNER_OFFSET = 30
_OUTER_MAX = 250
_ELECTRON_R = 4


class AtomWindow(tk.Toplevel):
    def __init__(self, parent: tk.Misc, element: Element) -> None:
        super().__init__(parent)
        self.title(f"Atom — {element.name}")
        self.transient(parent)

        canvas = tk.Canvas(
            self, width=_CANVAS_SIZE, height=_CANVAS_SIZE, bg="white", highlightthickness=0,
        )
        canvas.pack(padx=8, pady=8)
        self._draw(canvas, element)

    @staticmethod
    def _draw(canvas: tk.Canvas, element: Element) -> None:
        canvas.create_oval(
            _CENTER - _NUCLEUS_R, _CENTER - _NUCLEUS_R,
            _CENTER + _NUCLEUS_R, _CENTER + _NUCLEUS_R,
            fill="#444", outline="",
        )
        canvas.create_text(
            _CENTER, _CENTER,
            text=f"{element.symbol}\n{element.atomic_number}",
            fill="white", justify=tk.CENTER, font=("TkDefaultFont", 10, "bold"),
        )

        shells = fill_shells(element.atomic_number)
        k = len(shells)
        step = _OUTER_MAX // k

        for i, count in enumerate(shells, start=1):
            r = _INNER_OFFSET + i * step
            canvas.create_oval(
                _CENTER - r, _CENTER - r,
                _CENTER + r, _CENTER + r,
                outline="#888",
            )
            for n in range(count):
                theta = 2 * math.pi * n / count
                x = _CENTER + r * math.cos(theta)
                y = _CENTER + r * math.sin(theta)
                canvas.create_oval(
                    x - _ELECTRON_R, y - _ELECTRON_R,
                    x + _ELECTRON_R, y + _ELECTRON_R,
                    fill="#1f77b4", outline="",
                )
