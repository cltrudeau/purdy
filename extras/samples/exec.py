#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import Shell, Wait, AppendTypewriter
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

screen.run(actions)
