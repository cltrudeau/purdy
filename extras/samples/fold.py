#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the code folding mechanism

from purdy.actions import Append, Fold, Wait, Clear
from purdy.content import Code
from purdy.ui import SimpleScreen

code = Code('../display_code/code.py')

screen = SimpleScreen(starting_line_number=1)
box = screen.code_box

actions = [
    Append(box, code),
    Wait(),
    Fold(box, 20, 23),
    Wait(),
    Fold(box, 27),
    Wait(),
    Clear(box),           # test long fold without wait, used to crash
    Append(box, code),
    Fold(box, 2),
]

if __name__ == '__main__':
    screen.run(actions)
