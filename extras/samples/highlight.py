#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import AppendAll, Highlight
from purdy.content import CodeFile
from purdy.settings import settings
from purdy.ui import Screen

#settings['colour'] = 16
screen = Screen(settings, show_line_numbers=True)
code_box = screen.code_box
blob = CodeFile('../display_code/console2.py', 'con')

actions = [
    AppendAll(code_box, blob),
    Highlight(code_box, range(1, 45), True),
    Highlight(code_box, range(1, 45), False),
]

screen.run(actions)
