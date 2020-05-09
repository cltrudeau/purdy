#!/usr/bin/env python

# Example code for showing a top with code and a bottom with console

from purdy.actions import Append
from purdy.content import Code
from purdy.ui import Screen, CodeBox, TwinCodeBox

py_code = Code(filename='../display_code/code.py')
con_code = Code(filename='../display_code/console.repl')

screen = Screen(rows=[TwinCodeBox(left_starting_line_number=1, right_weight=2, 
    height=14), CodeBox(auto_scroll=False)])

actions = [
    Append(screen.code_boxes[0], py_code),
    Append(screen.code_boxes[1], con_code),
    Append(screen.code_boxes[2], con_code),
]

screen.run(actions)
