import pytest

tk = pytest.importorskip("tkinter")

from periodic_table.data import ELEMENTS  # noqa: E402
from periodic_table.views.atom_view import AtomWindow  # noqa: E402
from periodic_table.views.detail_window import ElementDetailWindow  # noqa: E402
from periodic_table.views.grid_view import PeriodicGridView  # noqa: E402
from periodic_table.views.search_bar import SearchBar  # noqa: E402


@pytest.fixture
def root():
    try:
        r = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk display unavailable: {exc}")
    r.withdraw()
    yield r
    r.destroy()


def test_smoke_construct_all_widgets(root):
    grid = PeriodicGridView(root, on_select=lambda _e: None)
    bar = SearchBar(root, on_change=grid.highlight)
    detail = ElementDetailWindow(root, ELEMENTS[0])   # Hydrogen
    atom = AtomWindow(root, ELEMENTS[-1])             # Oganesson
    grid.highlight("Na")
    grid.highlight("")
    assert bar is not None
    assert detail is not None
    assert atom is not None
