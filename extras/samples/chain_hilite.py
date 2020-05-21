#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates highlight chain action

from purdy.actions import Append, HighlightChain
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=1)
code_box = screen.code_box
blob = Code('../display_code/code.py')

actions = [
    Append(code_box, blob),
    HighlightChain(code_box, ['1-2', '3-4', '5-6', '7-8', '9-12']),
]

if __name__ == '__main__':
    screen.run(actions)
