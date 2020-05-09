#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import Append, Highlight, Wait
from purdy.content import Code
from purdy.settings import settings
from purdy.ui import SimpleScreen

#settings['colour'] = 16
screen = SimpleScreen(settings, starting_line_number=1)
code_box = screen.code_box
blob = Code('../display_code/console.repl')

actions = [
    Append(code_box, blob),
    Wait(),
    Highlight(code_box, range(5, 41), True),
    Wait(),
    Highlight(code_box, '5,6,10-20', False),
]

screen.run(actions)
