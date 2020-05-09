#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import Append
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
blob = Code('../display_code/console.repl')
action = Append(screen.code_box, blob)
screen.run([action])
