#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the code folding mechanism

from purdy.actions import Append, Fold, Wait
from purdy.content import Code
from purdy.ui import SimpleScreen

code = Code('../display_code/code.py')

screen = SimpleScreen(starting_line_number=10)
box = screen.code_box

actions = [
    Append(box, code),
    Wait(),
    Fold(box, 10, 13),
    Wait(),
    Fold(box, 27),
]

if __name__ == '__main__':
    screen.run(actions)
