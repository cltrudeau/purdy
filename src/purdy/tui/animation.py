# tui.animation.py
from copy import deepcopy

from purdy.tui.steps import AppendStep

# ===========================================================================
# Cells
# ===========================================================================

class Cell:
    def __init__(self, manager):
        self.steps = []
        self.manager = manager

    def forwards(self):
        for step in self.steps:
            step.forwards()

    def backwards(self):
        for step in self.steps:
            step.backwards()


class MultiCell:
    def __init__(self):
        self.steps = []
        self.current_step = 0

    def forwards(self, manager):
        manager.animating = True

    def next_step(self, manager):
        step = self.steps[self.current_step]
        step.forward(manager)

        self.current_step += 1
        if self.current_step >= len(self.steps):
            manager.animating = False
            return True

        return False

    def fast_forward(self, manager):
        for step in steps[self.current_step:]:
            step.forward(manager)

        manager.animating = False
        self.current_step = len(self.steps)

# ===========================================================================
# Manager
# ===========================================================================

class ActionManager:
    def __init__(self):
        self.started = False
        self.frame = None
        self.animating = False
        self.cells = []
        self.current_cell = 0

    # ----
    # Step Management

    def _append_steps(self, steps):
        if not self.cells:
            self.cells = [Cell(self)]

        if isinstance(self.cells[-1], MultiCell):
            self.cells.append(Cell(self))

        self.cells[-1].steps += steps

    def _end_cell(self):
        self.cells.append(Cell(self))

    def _append_multi_cell(self, steps):
        cell = MultiCell(self, steps)

        # Check if the last cell is empty, if so replace it
        if not self.cells[-1].steps:
            self.cells[-1] = cell
        else:
            self.cells.append(cell)

    def _forwards(self):
        self.started = True
        if self.current_cell >= len(self.cells):
            return

        cell = self.cells[self.current_cell]
        cell.forwards()
        self.current_cell += 1

    def _backwards(self):
        if not self.started or self.current_cell == 0:
            return

        self.current_cell -= 1
        cell = self.cells[self.current_cell]
        cell.backwards()

        if self.current_cell == 0:
            self.started = False

    # ----
    # Actions
    def append(self, box, *args):
        """Appends content to a given box. Accepts either
        :code:`purdy.content.Code` objects or strings. Strings are parsed as
        plain text.

        :param *args: one or more items to append
        """
        if len(args) == 0:
            raise ValueError("Must provide code to append")

        self._append_steps([AppendStep(box, *args)])
        return self

    def wait(self):
        self.cells.append(Cell(self))
        return self
