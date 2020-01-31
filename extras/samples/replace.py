#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import AppendAll, ReplaceAll, ReplaceTypewriter, Wait
from purdy.content import CodeFile
from purdy.ui import Screen

screen = Screen(show_line_numbers=True)
code_box = screen.code_box
blob = CodeFile('../display_code/simple.py', 'con')
blob2 = CodeFile('../display_code/console.py', 'con')

actions = [
    AppendAll(code_box, blob),
    Wait(),
    ReplaceAll(code_box, blob2),
    Wait(),
    ReplaceTypewriter(code_box, blob),
]

screen.run(actions)
