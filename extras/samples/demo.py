#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates many of the display features of the purdy library

from purdy.tui.screen import SimpleScreen
from purdy.content import Code

screen = SimpleScreen()
box = screen.box

INTRO = """\
Welcome to the purdy TUI. This program demonstrates some of the libraries
features. Press the right arrow key to see the next segment.

"""

(box.actions
    .append(INTRO)
    .wait()
)

SHORT = """\
# Purdy colourizes a variety of styles of code when you're done
# admiring this program, press the right arrow key.

def say_hello(name):
    print(f"Hello, {name}")

"""

code = Code(text=SHORT, parser="py")
box.actions.append(code)

screen.run()
#screen.print_steps()
