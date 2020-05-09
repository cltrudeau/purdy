#!/usr/bin/env python

# Example code for showing a top with code and a bottom with console

from purdy.actions import Append
from purdy.content import Code
from purdy.ui import Screen, CodeBox

py_code = Code('../display_code/code.py')
con_code = Code('../display_code/simple.repl')

screen = Screen(rows=[CodeBox(starting_line_number=1), CodeBox(height=7), 
    CodeBox(auto_scroll=False)])

actions = [
    Append(screen.code_boxes[0], py_code),
    Append(screen.code_boxes[1], con_code),
    Append(screen.code_boxes[2], py_code),
]

screen.run(actions)
