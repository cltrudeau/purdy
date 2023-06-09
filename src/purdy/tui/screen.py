#!/usr/bin/env python3

from asciimatics.widgets import Frame, Layout, Divider, PopUpDialog
from asciimatics.effects import Background
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.parsers import AsciimaticsParser

import sys
import logging

from purdy.tui.listing_box import ListingBox

# Test data
tree = r"""${1}This is the first wrapping line, wrap wrap wrap, and then wrap some more.  These are the Daves I know I know, these are the Daves I know
       ${3,1}*
${2}      / \
${2}     /${1}o${2}  \
${2}    /_   _\ ${1}
123456789 123456789 123456789 123456789 123456789abcdefgh
${2}     /   \${4}b
${2}    /     \
${2}   /   ${1}o${2}   \
${2}  /__     __\
  ${1}d${2} / ${4}o${2}   \
${2}   /       \
${2}  / ${4}o     ${1}o${2}.\
${2} /___________\
      ${3}|||
      ${3}|||

This is a very long line that goes on and on, it might wrap for you

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25""".split("\n")

extra = """\
26
27
28
29
30""".split("\n")

#tree = [c for c in "1234567890abcdefghijklmnop"]

# Initial data for the form
form_data = {
    "TA": tree + extra,
    #"TA": tree,
}

logging.basicConfig(filename="debug.log", level=logging.DEBUG)


def global_keyhandler(event):
    if isinstance(event, KeyboardEvent):
        if event.key_code == ord('q') or event.key_code == ord('Q'):
            raise StopApplication("User terminated app")


class DemoFrame(Frame):
    def __init__(self, screen):
        super(DemoFrame, self).__init__(screen, screen.height, screen.width,
            data=form_data, has_border=False, can_scroll=False)

        self.set_theme('monochrome')
        layout = Layout([1,], fill_frame=True)
        self.add_layout(layout)

        box = ListingBox(ListingBox.FILL_FRAME, name="TA",
            parser=AsciimaticsParser(), line_wrap=True)
        box.line_cursor = False
        layout.add_widget(box, 0)
        self.fix()


def frame_runner(screen, scene):
    scenes = [
        Scene([Background(screen), DemoFrame(screen) ], -1)
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene,
        unhandled_input=global_keyhandler, allow_int=True,)


def run(rows=[], actions=[]):
    last_scene = None
    while True:
        try:
            Screen.wrapper(frame_runner, catch_interrupt=False,
                arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
