#!/usr/bin/env python

### Example purdy library code
#
# Displays a colourized Python REPL session to the screen

from purdy.actions import Append
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
blob = Code('../display_code/console.repl')
actions = [
    Append(screen.code_box, blob),
]

if __name__ == '__main__':
    screen.run(actions)
