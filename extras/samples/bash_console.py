#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import AppendTypewriter
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code_box = screen.code_box
blob = Code('../display_code/curl.bash')
action = AppendTypewriter(code_box, blob)
screen.run([action])
