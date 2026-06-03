import tkinter as tk

from periodic_table.model import Element


_FIELDS: tuple[tuple[str, str | None], ...] = (
    ("Name",                "name"),
    ("Symbol",              "symbol"),
    ("Atomic number",       "atomic_number"),
    ("Atomic mass",         "mass"),
    ("Period",              "period"),
    ("Group",               "group"),
    ("Category",            None),
    ("Electron config",     "electron_config"),
    ("Electronegativity",   "electronegativity"),
    ("Phase",               "phase"),
)


def _value(element: Element, attr: str | None) -> object:
    if attr is None:
        return element.category.value
    return getattr(element, attr)


def _fmt(value: object) -> str:
    return "—" if value is None else str(value)


def _diff_label(a: object, b: object) -> str:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        delta = b - a
        sign = "+" if delta >= 0 else ""
        return f"{sign}{delta:g}"
    return "✓" if a == b else "≠"


class ComparisonWindow(tk.Toplevel):
    def __init__(self, parent: tk.Misc, left: Element, right: Element) -> None:
        super().__init__(parent)
        self.title(f"Compare — {left.symbol} vs {right.symbol}")
        self.transient(parent)

        body = tk.Frame(self, padx=14, pady=14)
        body.pack(fill=tk.BOTH, expand=True)

        header_font = ("TkDefaultFont", 11, "bold")
        tk.Label(body, text="", width=20).grid(row=0, column=0)
        tk.Label(body, text=f"{left.name} ({left.symbol})",
                 font=header_font, anchor="w").grid(row=0, column=1, sticky="w", padx=8)
        tk.Label(body, text=f"{right.name} ({right.symbol})",
                 font=header_font, anchor="w").grid(row=0, column=2, sticky="w", padx=8)
        tk.Label(body, text="Δ", font=header_font).grid(row=0, column=3, padx=8)

        for i, (label, attr) in enumerate(_FIELDS, start=1):
            la = _value(left, attr)
            ra = _value(right, attr)
            tk.Label(body, text=f"{label}:", anchor="e", width=20).grid(
                row=i, column=0, sticky="e", padx=(0, 8), pady=1,
            )
            differ = la != ra
            color = "#d35400" if differ else "black"
            tk.Label(body, text=_fmt(la), anchor="w", fg=color).grid(
                row=i, column=1, sticky="w", padx=8, pady=1,
            )
            tk.Label(body, text=_fmt(ra), anchor="w", fg=color).grid(
                row=i, column=2, sticky="w", padx=8, pady=1,
            )
            delta_color = color if differ else "#888"
            tk.Label(body, text=_diff_label(la, ra), fg=delta_color).grid(
                row=i, column=3, padx=8, pady=1,
            )
