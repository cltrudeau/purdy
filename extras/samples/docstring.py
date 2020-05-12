#!/usr/bin/env python

### Example purdy library code
#
# Displays a function with a multi-line doc string (these can be tricky to
# parse, want to make sure each line is colourized as a string)

from purdy.actions import Append
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
blob = Code('../display_code/docstring.py')
actions = [
    Append(screen.code_box, blob),
]

if __name__ == '__main__':
    screen.run(actions)
