#!/usr/bin/env python
"""
Animation Management
====================

This module handles the slide rendering animation in the urwid purdy player
"""
from enum import Enum

import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)
logger = logging.getLogger()

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
        """Register one or more "cell" classes from 
        :mod:`purdy.animation.cell` objects to be animated. 

        :param content: a single Cell or iterable of them
        """
        if isinstance(content, list) or isinstance(content, tuple):
            for cell in content:
                self.cells.append(cell)
        else:
            self.cells.append(content)

    def _conditional_alarms(self, cell):
        # if we're in movie mode and the cell isn't doing a typewriter
        # animation, wake us up for the next animation
        if not cell.is_animating and self.screen.movie_mode > -1:
            self.screen.set_alarm('movie_alarm', self.screen.movie_mode)

    def auto_forward_alarm(self):
        self.state = self.State.ACTIVE
        self.forward()

    def animation_alarm(self):
        self.state = self.State.ACTIVE
        cell = self.cells[self.index]
        cell.animation_wake_up(self)
        self._conditional_alarms(cell)

    def movie_alarm(self):
        self.State.ACTIVE
        self.forward()
        
    def perform(self, key):
        logger.debug('AM.perform(%s), %s', key, self.state)
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

        if not cell.auto_forward:
            self._conditional_alarms(cell)

    def fast_forward(self):
        if self.index + 1 >= len(self.cells):
            return

        self.index += 1
        self.cells[self.index].render(self, skip=True)

    def interrupt(self):
        logger.debug('AM.interrupt(), %s', self.cells[self.index])
        self.cells[self.index].interrupt(self)

    def backward(self):
        if self.index <= 0:
            return

        self.cells[self.index].undo(self)
        self.index -= 1
