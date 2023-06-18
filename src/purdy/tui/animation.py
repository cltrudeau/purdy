# tui.animation.py
from copy import deepcopy

from purdy.tui.steps import AppendStep

# ===========================================================================
# Cells
# ===========================================================================

class Cell:
    def __init__(self):
        self.steps = []

    def forward(self):
        for step in self.steps:
            step.forward()

        return 1

    def fast_forward(self):
        # No animation, skip and next are the same
        return self.forward()

    def backward(self):
        for step in self.steps:
            step.backward()


class MultiCell:
    def __init__(self):
        self.steps = []
        self.current_step = 0

    def forward(self):
        global animator
        animator.animating = True

        step = self.steps[self.current_step]
        step.forward()

        self.current_step += 1
        if self.current_step >= len(self.steps):
            animator.animating = False
            return 1

        return 0

    def fast_forward(self):
        # Turn off animation and complete all remaining steps
        global animator
        animator.animating = False

        for step in steps[self.current_step:]:
            step.forward()

        self.current_step = len(self.steps)
        return 1

    def backward(self, manager):
        # Turn off animation and undo all preformed steps
        global animator
        animator.animating = False

        for step in self.steps:
            step.backward()

# ===========================================================================
# Animator
# ===========================================================================

class Animator:
    def __init__(self):
        self.started = False
        self.animating = False
        self.cells = []
        self.current_cell = 0

    # ----
    # Step Management

    def append_steps(self, steps):
        if not self.cells:
            self.cells = [Cell()]

        if isinstance(self.cells[-1], MultiCell):
            self.cells.append(Cell())

        self.cells[-1].steps += steps

    def end_cell(self):
        self.cells.append(Cell())

    def append_multi_cell(self, steps):
        cell = MultiCell(self)
        cell.steps += steps

        # Check if the last cell is empty, if so replace it
        if not self.cells[-1].steps:
            self.cells[-1] = cell
        else:
            self.cells.append(cell)

    def forward(self):
        self.started = True
        if self.current_cell >= len(self.cells):
            return

        cell = self.cells[self.current_cell]
        delta = cell.forward()
        self.current_cell += delta

    def fast_forward(self):
        self.started = True
        if self.current_cell >= len(self.cells):
            return

        cell = self.cells[self.current_cell]
        cell.fast_forward()
        self.current_cell += 1

    def backward(self):
        if not self.started or self.current_cell == 0:
            return

        self.current_cell -= 1
        cell = self.cells[self.current_cell]
        cell.backward()

        if self.current_cell == 0:
            self.started = False

animator = Animator()

# ===========================================================================
# Action Manager
# ===========================================================================

class ActionManager:
    def __init__(self, box):
        self.box = box

    # ----
    # Actions
    def append(self, *args):
        """Appends content to the associated box. Accepts either
        :code:`purdy.content.Code` objects or strings. Strings are parsed as
        plain text.

        :param *args: one or more items to append
        """
        if len(args) == 0:
            raise ValueError("Must provide code to append")

        animator.append_steps([AppendStep(self.box, *args)])
        return self

    def wait(self):
        animator.cells.append(Cell())
        return self
