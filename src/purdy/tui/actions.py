# tui.actions.py
"""This module contains the animation actions you can use to build a slideshow
using the purdy library. Actions are passed in to the `.run()` method of your
:class:`purdy.tui.screen.Screen` object.
"""

# ===========================================================================

from purdy.tui.steps import AppendStep

# ===========================================================================

class Append:
    def __init__(self, box, item):
        step = AppendStep(

        box.manager.cells.append(cell)

