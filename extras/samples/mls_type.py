#!/usr/bin/env python

### Example purdy library code
#
# Example of a multi-line string in a Python REPL session using the typewriter
# animation.

from purdy.actions import AppendTypewriter
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code_box = screen.code_box
blob = Code('../display_code/mls.repl')

actions = [
    AppendTypewriter(code_box, blob),
    AppendTypewriter(code_box, blob),
]

if __name__ == '__main__':
    screen.run(actions)
