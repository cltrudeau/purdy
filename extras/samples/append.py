#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import Append, Wait
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=1)
code_box = screen.code_box
blob = Code('../display_code/simple.repl')

actions = [
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
    Append(code_box, blob),
    Wait(),
]

if __name__ == '__main__':
    screen.run(actions)
