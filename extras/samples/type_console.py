#!/usr/bin/env python

from purdy.actions import AppendTypewriter
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code_box = screen.code_box
blob = Code('../display_code/console.repl')
action = AppendTypewriter(code_box, blob)
screen.run([action])
