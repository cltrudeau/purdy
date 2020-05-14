#!/usr/bin/env python
"""
Animation Cells
===============

A Cell represents an animation used by the
:class:`purdy.animation.manager.AnimationManager`. A Cell is responsible for
rendering or undoing work to a :class:`purdy.widget.CodeBox`. Animating cells
can partially render then wait for an alarm provided by the manager to continue
rendering.
"""
from copy import deepcopy
from enum import Enum

from purdy.animation import steps as steplib
from purdy.parser import BlankCodeLine, parse_source

# ===========================================================================
# Cell Factory
# ===========================================================================

def group_steps_into_cells(steps):
    """Actions create multiple steps possibly with cell breaks between them.
    This method takes a list of steps and returns a list of Cell objects,
    grouping the steps by break marker

    :param steps: a list of steps
    :returns: a list of Cell objects
    """
    cells = []
    cell = None
    for step in steps:
        if isinstance(step, steplib.CellEnd):
            if cell:
                cells.append(cell)

            cell = None
        elif isinstance(step, steplib.Transition):
            if cell:
                cells.append(cell)

            cell = TransitionCell(step.code_box, step.code)
            cells.append(cell)
            cell = None
        else:
            if not cell:
                cell = GroupCell()

            cell.steps.append(step)

    if cell and len(cell.steps) > 0:
        cells.append(cell)

    return cells

# ===========================================================================
# Base Classes
# ===========================================================================

class AnimatingCellBase:
    @property
    def is_animating(self):
        return self.animation_alarm_handle is not None

    def animation_wake_up(self, manager):
        self.animation_alarm_handle = None
        self.render(manager)

    def interrupt(self, manager):
        # interrupted during an animation sequence, remove the timer
        manager.screen.loop.remove_alarm(self.animation_alarm_handle)

        self.animation_alarm_handle = None
        manager.state = manager.State.ACTIVE
        self.render(manager, skip=True)

# ===========================================================================
# Cells
# ===========================================================================

class GroupCell(AnimatingCellBase):
    """Groups steps together into a bundle that can be rendered or undone
    together. Implements animation alarms so the manager can do timed call
    backs into the group and continue rendering.
    """
    def __init__(self):
        self.steps = []
        self.index = 0
        self.animation_alarm_handle = None

    def __str__(self):
        step_string = ','.join([str(step) for step in self.steps])
        return 'GroupCell(steps=[' + step_string + '])'

    def _test_dict(self):
        d = {
            'GroupCell': {
                'steps':[step._test_dict() for step in self.steps],
            }
        }

        return d

    def render(self, manager, skip=False):
        if len(self.steps) == 0 or self.index >= len(self.steps):
            # badly formed action sequences that result in an empty cell would
            # cause a crash, just do nothing
            return

        for x in range(self.index, len(self.steps)):
            self.index = x
            step = self.steps[x]

            if isinstance(step, steplib.Sleep):
                if skip:
                    # in fast-forward mode, do nothing with this Sleep
                    continue
                else:
                    manager.state = manager.State.SLEEPING
                    loop = manager.screen.loop
                    self.animation_alarm_handle = loop.set_alarm_in(step.time, 
                            manager.screen.base_window.animation_alarm)
                    self.index += 1
                    return

            try:
                step.render_step()
            except steplib.StopMovieException:
                manager.screen.movie_mode = -1

    def undo(self, manager):
        if len(self.steps) == 0:
            # badly formed action sequences that result in an empty cell would
            # cause a crash, just do nothing
            return

        # if we rendered everything and the last call was a Sleep, the index
        # may be past our list bounds
        if self.index >= len(self.steps):
            self.index = len(self.steps) - 1

        for x in range(self.index, -1, -1):
            self.index = x
            step = self.steps[x]
            if not isinstance(step, steplib.Sleep):
                step.undo_step()


class TransitionCell(AnimatingCellBase):
    DELAY = 0.05
    BETWEEN_DELAY = 0.3

    class State(Enum):
        BEFORE = 0
        DELETING = 1
        APPENDING = 2
        DONE = 3

    def __init__(self, code_box, code):
        self.code_box = code_box
        self.code = code
        self.state = self.State.BEFORE
        self.steps = []

    def _test_dict(self):
        d = {
            'TransitionCell': {
                'code':f'{self.code.source}',
            }
        }

        return d

    def render(self, manager, skip=False):
        if self.state == self.State.DONE:
            return

        delay = self.DELAY
        if self.state == self.State.BEFORE:
            # first time through, setup our append and undo lines
            self.position = 1
            self.code_lines = parse_source(self.code.source, self.code.lexer)
            self.undo_lines = deepcopy(self.code_box.listing.lines)

            self.state = self.State.DELETING
            # intentional fall through

        if self.state == self.State.DELETING:
            if self.position >= len(self.code_box.listing.lines):
                # wiped everything, delete the empty boxes and go into append 
                # mode
                self.code_box.listing.clear()
                self.state = self.State.APPENDING
                delay = self.BETWEEN_DELAY
            else:
                line = BlankCodeLine()
                self.code_box.listing.replace_line(self.position, line)
                self.position += 1
        else: # state == APPENDING
            try:
                line = self.code_lines.pop(0)
                self.code_box.listing.insert_lines(0, [line, ])
            except IndexError:
                self.state = self.State.DONE
                return

        # ask to be woken back up for the next step
        manager.state = manager.State.SLEEPING
        loop = manager.screen.loop
        self.animation_alarm_handle = loop.set_alarm_in(delay,
            manager.screen.base_window.animation_alarm)

    def undo(self, manager):
        self.state = self.State.BEFORE
        self.code_box.listing.clear()
        self.code_box.listing.insert_lines(0, self.undo_lines)
