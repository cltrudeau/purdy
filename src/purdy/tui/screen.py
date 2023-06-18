#!/usr/bin/env python3

import sys
import logging

from dataclasses import dataclass

from asciimatics.effects import Background
from asciimatics.event import KeyboardEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen as MaticsScreen
from asciimatics.exceptions import ResizeScreenError, StopApplication

from purdy.content import Listing
from purdy.tui.animation import ActionManager, animator
from purdy.tui.widgets import PurdyFrame, ListingBox

logging.basicConfig(filename="debug.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ===========================================================================

@dataclass
class CodeBox:
    height: int = None
    width_ratio: float = 1.0
    starting_line_number: int = None
    auto_scroll: bool = True

    """Defines a box to display code in. Two boxes can form a pair in a row by
    passing a tuple containing them to the screen.

    :param height: height of the box in lines, defaults to None to
                   automatically determine the height. Note that only the left
                   most box height is used when pairing boxes

    :param width_ration: a float value indicating how wide this box is in
                         comparison to its pair when this box has a pair in
                         the same row. A value of 0.5 makes both boxes the
                         same width. Defaults to 1.0, ignored if not used in a
                         pairing

    :param starting_line_number: the number to start with if displaying line
                                 numbers. Defaults to None to turn numbers off

    :param auto_scroll: True if the corresponding widget should scroll to the
                        bottom when something new is added. Defaults to True.
    """

    def __post_init__(self):
        self.listing = Listing(starting_line_number=self.starting_line_number)
        self.actions = ActionManager(self)

        logger.debug("Created CodeBox, listing id=%s", id(self.listing))

# ===========================================================================

class _BaseScreen:
    def __init__(self, rows):
        self.rows = rows
        self.boxes = {}

        for index, item in enumerate(rows):
            name = f"box{index}"
            if isinstance(item, tuple):
                item[0].name = name + "_0"
                self.boxes[item[0].name] = item[0]

                item[1].name = name + "_1"
                self.boxes[item[1].name] = item[1]
            else:
                item.name = name
                self.boxes[name] = item

# ===========================================================================

class Screen(_BaseScreen):
    def __init__(self, rows, max_height=None):
        self.max_height = max_height
        super().__init__(rows)

    def _global_keyhandler(self, event):
        if not isinstance(event, KeyboardEvent):
            return

        if event.key_code == ord('q') or event.key_code == ord('Q'):
            raise StopApplication("User terminated app")

    def _frame_runner(self, matics_screen, scene):
        scenes = [
            Scene(
                [   Background(matics_screen),
                    PurdyFrame(self.rows, matics_screen, self.max_height)
                ], -1
            )
        ]

        matics_screen.play(scenes, stop_on_resize=True, start_scene=scene,
            unhandled_input=self._global_keyhandler, allow_int=True,)

    def run(self):
        last_scene = None
        while True:
            try:
                MaticsScreen.wrapper(self._frame_runner, catch_interrupt=False,
                    arguments=[last_scene])
                sys.exit(0)
            except ResizeScreenError as e:
                last_scene = e.scene

    def print_steps(self):
        # Prints out debug information about the animation sequences
        global animator
        print("****", animator.cells)
        for cell in animator.cells:
            print(cell.__class__.__name__)

            for step in cell.steps:
                print(step)

# ===========================================================================


class SimpleScreen(Screen):
    """Convenience implementation of :class:`Screen` that supports a single
    :class:`CodeBox`.  The code box is available as
    :attr:`SimpleScreen.code_box`.

    :param starting_line_number: starting line number for the created code box,
                                 defaults to None for no numbers
    :param auto_scroll: When True, the class:`ui.CodeBox` automatically
                        scrolls to newly added content.  Defaults to True.

    :param max_height: maximum display height in TUI mode, defaults to 0,
                       meaning no max
    """
    def __init__(self, starting_line_number=None, auto_scroll=True,
            max_height=None):

        self.box = CodeBox(starting_line_number=starting_line_number,
            auto_scroll=auto_scroll)

        super().__init__([self.box], max_height)


class SplitScreen(Screen):
    """Convenience implementation of :class:`Screen` that supports two
    :class:`CodeBox` instances, stacked vertically and separated by a dividing
    line. The code boxes are :attr:`SplitScreen.top` and
    :attr:`SplitScreen.bottom`.

    :param settings: a settings dictionary object. Defaults to `None` which
                     uses the default settings dictionary:
                     :attr:`settings.settings`

    :param top_starting_line_number: starting line number for the top code box,
                                     defaults to None for no line numbers

    :param top_auto_scroll: When True, the top :class:`ui.CodeBox` automatically
                            scrolls to newly added content.  Defaults to True.

    :param top_height: Number of lines the top box should be. A value of None
                       indicates top and bottom should be the same size.
                       Defaults to None.

    :param bottom_starting_line_number: starting line number for the bottom
                                        code box, defaults to None for no line
                                        numbers

    :param bottom_auto_scroll: When True, the bottom :class:`ui.CodeBox`
                            automatically scrolls to newly added content.
                            Defaults to True.

    :param max_height: maximum display height in TUI mode, defaults to None,
                       meaning no max
    """
    def __init__(self, top_starting_line_number=None, top_auto_scroll=True,
            top_height=None, bottom_starting_line_number=None,
            bottom_auto_scroll=True, max_height=None):

        self.top = CodeBox(starting_line_number=top_starting_line_number,
            height=top_height, auto_scroll=top_auto_scroll)
        self.bottom = CodeBox(starting_line_number=bottom_starting_line_number,
            auto_scroll=bottom_auto_scroll)
        super().__init__(rows=[self.top, self.bottom], max_height=max_height)
