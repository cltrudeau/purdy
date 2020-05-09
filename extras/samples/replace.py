#!/usr/bin/env python

from purdy.actions import Append, Clear, Wait
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=10)
code_box = screen.code_box
blob = Code('../display_code/simple.repl')
blob2 = Code('../display_code/traceback.repl')

actions = [
    Append(code_box, blob),
    Wait(),
    Clear(code_box),
    Append(code_box, blob2),
]

screen.run(actions)
