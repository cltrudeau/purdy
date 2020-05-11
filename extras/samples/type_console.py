#!/usr/bin/env python

from purdy.actions import AppendTypewriter
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code_box = screen.code_box
blob = Code('../display_code/console.repl')
actions = [
    AppendTypewriter(code_box, blob),
]

if __name__ == '__main__':
    screen.run(actions)
