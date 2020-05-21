#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the slide transition animation

from purdy.actions import Append, Wait, Transition
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=10)
code_box = screen.code_box
blob = Code('../display_code/simple.repl')
blob2 = Code('../display_code/traceback.repl')
blob3 = Code('../display_code/decorator.repl')

actions = [
    Append(code_box, blob2),
    Wait(),
    Transition(code_box, blob),
    Append(code_box, blob2),
    Wait(),
    Transition(code_box, blob3), # Test Wait after Transition
    Wait(),
    Append(code_box, blob2),
]

if __name__ == '__main__':
    screen.run(actions)
