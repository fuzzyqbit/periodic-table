import random
import time
import tkinter as tk
from typing import Callable

from periodic_table.data import ELEMENTS
from periodic_table.model import Element


class QuizWindow(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        attach_click_handler: Callable[[Callable[[Element], None]], None],
        detach_click_handler: Callable[[], None],
        flash_cell: Callable[[int, str, int], None],
    ) -> None:
        super().__init__(parent)
        self.title("Quiz — Find the Element")
        self.transient(parent)
        self.resizable(False, False)

        self._attach = attach_click_handler
        self._detach = detach_click_handler
        self._flash = flash_cell

        self._target: Element | None = None
        self._round_started_at: float | None = None
        self._score = 0
        self._attempts = 0
        self._timer_job: str | None = None

        body = tk.Frame(self, padx=16, pady=16)
        body.pack()

        tk.Label(body, text="Click the element shown below.",
                 font=("TkDefaultFont", 12)).pack(pady=(0, 8))

        self._prompt = tk.Label(body, text="Press Start", font=("TkDefaultFont", 18, "bold"))
        self._prompt.pack(pady=(0, 8))

        self._timer_label = tk.Label(body, text="0.0 s", font=("TkDefaultFont", 11))
        self._timer_label.pack()

        self._score_label = tk.Label(body, text="Score: 0 / 0")
        self._score_label.pack(pady=(0, 12))

        self._action = tk.Button(body, text="Start", command=self._start_or_next)
        self._action.pack()

        self.protocol("WM_DELETE_WINDOW", self._close)

    def _start_or_next(self) -> None:
        self._target = random.choice(ELEMENTS)
        self._round_started_at = time.monotonic()
        self._prompt.configure(
            text=f"Find: {self._target.name}  ({self._target.symbol}, Z={self._target.atomic_number})"
        )
        self._action.configure(text="Skip", command=self._skip)
        self._attach(self._on_grid_click)
        self._tick()

    def _tick(self) -> None:
        if self._round_started_at is None:
            return
        elapsed = time.monotonic() - self._round_started_at
        self._timer_label.configure(text=f"{elapsed:0.1f} s")
        self._timer_job = self.after(100, self._tick)

    def _stop_tick(self) -> None:
        if self._timer_job is not None:
            self.after_cancel(self._timer_job)
            self._timer_job = None

    def _on_grid_click(self, picked: Element) -> None:
        if self._target is None:
            return
        correct = picked.atomic_number == self._target.atomic_number
        self._attempts += 1
        if correct:
            self._score += 1
            self._flash(picked.atomic_number, "#2ecc71", 400)
            self._end_round(correct=True)
        else:
            self._flash(picked.atomic_number, "#e74c3c", 400)
            # leave target unchanged so player can try again

    def _skip(self) -> None:
        if self._target is None:
            return
        self._attempts += 1
        self._end_round(correct=False)

    def _end_round(self, correct: bool) -> None:
        self._stop_tick()
        self._detach()
        self._target = None
        self._round_started_at = None
        self._score_label.configure(text=f"Score: {self._score} / {self._attempts}")
        suffix = " — correct!" if correct else " — skipped."
        self._prompt.configure(text=self._prompt.cget("text") + suffix)
        self._action.configure(text="Next", command=self._start_or_next)

    def _close(self) -> None:
        self._stop_tick()
        self._detach()
        self.destroy()
