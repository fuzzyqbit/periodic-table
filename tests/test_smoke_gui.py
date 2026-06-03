import pytest

tk = pytest.importorskip("tkinter")

from periodic_table.data import ELEMENTS  # noqa: E402
from periodic_table.views.atom_view import AtomWindow  # noqa: E402
from periodic_table.views.compare import ComparisonWindow  # noqa: E402
from periodic_table.views.detail_window import ElementDetailWindow  # noqa: E402
from periodic_table.views.grid_view import PeriodicGridView  # noqa: E402
from periodic_table.views.legend import CategoryLegend  # noqa: E402
from periodic_table.views.quiz import QuizWindow  # noqa: E402
from periodic_table.views.search_bar import SearchBar  # noqa: E402
from periodic_table.views.timeline import TimelineSlider  # noqa: E402


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
    grid = PeriodicGridView(
        root,
        on_select=lambda _e: None,
        on_compare=lambda _a, _b: None,
    )
    bar = SearchBar(root, on_change=grid.highlight)
    legend = CategoryLegend(root)
    detail = ElementDetailWindow(root, ELEMENTS[0])     # Hydrogen
    atom = AtomWindow(root, ELEMENTS[-1])               # Oganesson
    comparison = ComparisonWindow(root, ELEMENTS[0], ELEMENTS[25])  # H vs Fe
    quiz = QuizWindow(
        root,
        attach_click_handler=grid.set_click_handler,
        detach_click_handler=grid.reset_click_handler,
        flash_cell=grid.flash_cell,
    )
    timeline = TimelineSlider(root, on_year_change=grid.filter_by_year)
    grid.highlight("Na")
    grid.highlight("")
    grid.flash_cell(1, "#00ff00", 50)
    grid.set_click_handler(lambda _e: None)
    grid.reset_click_handler()
    grid.filter_by_year(1800)
    grid.filter_by_year(2025)
    for widget in (bar, legend, detail, atom, comparison, quiz, timeline):
        assert widget is not None
