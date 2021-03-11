#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the Sleep action

from purdy.actions import Append, Sleep, Wait
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=10)
code_box = screen.code_box
blob = Code('../display_code/simple.repl')

actions = [
    Append(code_box, blob),
    Sleep(1),
    Append(code_box, blob),
    Sleep((3, 6)),
    Append(code_box, blob),
]

if __name__ == '__main__':
    screen.run(actions)
