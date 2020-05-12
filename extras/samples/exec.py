#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the Shell action that runs a subprocess and returns the result

from purdy.actions import Shell, AppendTypewriter
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code_box = screen.code_box

blob = Code(text="$ ls")
blob2 = Code(text="$ ls -la")

actions = [
    AppendTypewriter(code_box, blob),
    Shell(code_box, "ls"),
    AppendTypewriter(code_box, blob2),
    Shell(code_box, "ls -la"),
]

if __name__ == '__main__':
    screen.run(actions)
