import tkinter as tk

from periodic_table.model import Element
from periodic_table.views.atom_view import AtomWindow


def _fmt(value: object) -> str:
    return "—" if value is None else str(value)


class ElementDetailWindow(tk.Toplevel):
    _FIELDS: tuple[tuple[str, str], ...] = (
        ("Name",                "name"),
        ("Symbol",              "symbol"),
        ("Atomic number",       "atomic_number"),
        ("Atomic mass",         "mass"),
        ("Period",              "period"),
        ("Group",               "group"),
        ("Category",            None),  # special-cased: enum.value
        ("Electron config",     "electron_config"),
        ("Electronegativity",   "electronegativity"),
        ("Phase",               "phase"),
    )

    def __init__(self, parent: tk.Misc, element: Element) -> None:
        super().__init__(parent)
        self.title(element.name)
        self.transient(parent)

        body = tk.Frame(self, padx=12, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        for row, (label, attr) in enumerate(self._FIELDS):
            tk.Label(body, text=f"{label}:", anchor="e", width=20).grid(
                row=row, column=0, sticky="e", padx=(0, 8), pady=2,
            )
            if attr is None:
                value: object = element.category.value
            else:
                value = getattr(element, attr)
            tk.Label(body, text=_fmt(value), anchor="w").grid(
                row=row, column=1, sticky="w", pady=2,
            )

        tk.Button(
            body, text="Show atom",
            command=lambda: AtomWindow(self, element),
        ).grid(row=len(self._FIELDS), column=0, columnspan=2, pady=(12, 0))
