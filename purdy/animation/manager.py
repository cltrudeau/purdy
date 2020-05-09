#!/usr/bin/env python
"""
Animation Management
--------------------

This module handles the slide rendering animation in the urwid purdy player
"""
from enum import Enum

from .cell import Cell

# ==========================================================================
# Animation Manager
# ==========================================================================

class AnimationManager:
    class State(Enum):
        ACTIVE = 0
        SLEEPING = 1

    handled_keys = ['left', 'right', 's']

    def __init__(self, screen):
        self.screen = screen
        self.cells = []
        self.index = -1

    def register(self, content):
        """Register one or more :class:`purdy.animation.cell.Cell`
        objects to be animated. 

        :param content: a single Cell or iterable of them
        """
        if isinstance(content, Cell):
            self.cells.append(content)
        else:
            for cell in content:
                self.cells.append(cell)

    def _conditional_alarms(self, cell):
        # if we're in movie mode and the cell isn't doing a typewriter
        # animation, wake us up for the next animation
        no_typewriter = cell.typewriter_alarm_handle is None
        if no_typewriter and self.screen.movie_mode > -1:
            self.screen.loop.set_alarm_in(self.screen.movie_mode, 
                self.screen.base_window.movie_alarm)

    def first_wake_up(self):
        self.state = self.State.ACTIVE
        self.forward()

    def animation_wake_up(self):
        self.state = self.State.ACTIVE
        cell = self.cells[self.index]
        cell.typewriter_wake_up(self)
        self._conditional_alarms(cell)

    def movie_wake_up(self):
        self.State.ACTIVE
        self.forward()
        
    def perform(self, key):
        if key == 's' and self.state == self.State.SLEEPING:
            self.interrupt()
            return

        if self.state == self.State.SLEEPING:
            # ignore key presses while asleep
            return

        if key == 'right':
            self.forward()
        elif key == 'left':
            self.backward()
        elif key == 's':
            self.fast_forward()

    def forward(self):
        if self.index + 1 >= len(self.cells):
            return

        self.index += 1
        cell = self.cells[self.index]
        cell.render(self)
        self._conditional_alarms(cell)

    def fast_forward(self):
        if self.index + 1 >= len(self.cells):
            return

        self.index += 1
        self.cells[self.index].render(self, skip=True)

    def interrupt(self):
        self.cells[self.index].interrupt(self)

    def backward(self):
        if self.index <= 0:
            return

        self.cells[self.index].undo(self)
        self.index -= 1
