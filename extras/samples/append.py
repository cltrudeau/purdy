#!/usr/bin/env python

### Example purdy library code
#
# Appends the same colourized Python REPL session to the screen multiple
# times, waiting for a keypress between each

from purdy.actions import Append, Wait
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=1)
code_box = screen.code_box
blob = Code('../display_code/simple.repl')

actions = [
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
]

if __name__ == '__main__':
    screen.run(actions)
