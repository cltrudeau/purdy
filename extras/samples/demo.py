#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates many of the display features of the purdy library

from purdy.tui.screen import SimpleScreen
from purdy.content import Code


def message(box, text):
    (box.actions
        .append(text + "\n\n")
        .wait()
    )


screen = SimpleScreen()
box = screen.box


TEXT = """\
Welcome to the purdy TUI. This program demonstrates some of the libraries
features. Press the right arrow key to see the next segment."""

message(box, TEXT)

TEXT = """\
# Purdy colourizes a variety of styles of code when you're done
# admiring this program, press the right arrow key.

def say_hello(name):
    print(f"Hello, {name}")

"""

code = Code(text=TEXT, parser="py")
(box.actions
    .append(code)
    .wait()
)

TEXT = """\
Lines can be highlighted either through code or by typing a line number
and then pressing 'h'

"""

(box.actions
    .append(TEXT)
    .highlight(1, 7)
    .wait()
)

message(box, "All highlighting can be turned off by pressing 'H'")

TEXT = """\
The `highlight_chain` action is a short cut to turn highlighting on and
then off for a series of lines

"""

(box.actions
    .append(TEXT)
    .highlight_chain(8, '4-5')
    .wait()
)

message(box,  "The help screen can be shown by pressing '?'")


message(box,  "You can quit by pressing 'q'")

screen.run()
#screen.print_steps()
