#!/usr/bin/env python

### Example purdy library code
#
# Shows a split screen session with two code boxes on top and a third below.

from purdy.actions import Append, AppendTypewriter
from purdy.content import Code
from purdy.ui import Screen, CodeBox, TwinCodeBox

py_code = Code(filename='../display_code/decorator.repl')
con_code = Code(filename='../display_code/console.repl')

screen = Screen(rows=[TwinCodeBox(left_starting_line_number=1, right_weight=2, 
    height=14), CodeBox(auto_scroll=False)])

actions = [
    AppendTypewriter(screen.code_boxes[0], py_code),
    Append(screen.code_boxes[1], con_code),
    Append(screen.code_boxes[2], con_code),
]

if __name__ == '__main__':
    screen.run(actions)
