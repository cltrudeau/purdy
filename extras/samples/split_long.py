#!/usr/bin/env python

# Example code for showing a top with code and a bottom with console

from purdy.actions import Append
from purdy.content import Code
from purdy.ui import SplitScreen

code1 = Code('../display_code/console.repl')
code2 = Code('../display_code/console.repl')

screen = SplitScreen()

actions = [
    Append(screen.code_boxes[0], code1),
    Append(screen.code_boxes[1], code2),
]

screen.run(actions)
