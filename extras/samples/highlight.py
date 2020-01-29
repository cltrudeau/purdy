#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import AppendAll, Highlight
from purdy.content import CodeBlob
from purdy.ui import Screen

screen = Screen(show_line_numbers=True)
code_box = screen.code_box
blob = CodeBlob('../display_code/simple.py', 'con')

actions = [
    AppendAll(code_box, blob),
    Highlight(code_box, 1, True),
    Highlight(code_box, 1, False),
    Highlight(code_box, (2, 3), True),
]

screen.run(actions)
