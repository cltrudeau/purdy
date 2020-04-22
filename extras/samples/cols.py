#!/usr/bin/env python

# Example code for showing a top with code and a bottom with console

from purdy.actions import AppendAll
from purdy.content import CodeFile
from purdy.ui import RowScreen, Box, TwinBox

py_code = CodeFile('../display_code/code.py', 'py3')
con_code = CodeFile('../display_code/console2.repl', 'con')

screen = RowScreen(rows=[TwinBox(left_line_numbers=True, height=14), 
    Box(auto_scroll=False)])

actions = [
    AppendAll(screen.code_boxes[0], py_code),
    AppendAll(screen.code_boxes[1], con_code),
    AppendAll(screen.code_boxes[2], con_code),
]

screen.run(actions)
