#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates removing lines of code

from purdy.actions import Append, Wait, Remove
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=1)
code_box = screen.code_box
blob = Code('../display_code/code.py')

actions = [
    Append(code_box, blob),
    Wait(),
    Remove(code_box, 10, 4),
    Wait(),
    Remove(code_box, 12, 1),
    Wait(),
    Remove(code_box, 15, 3),
]

if __name__ == '__main__':
    screen.run(actions)
