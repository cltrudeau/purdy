#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import AppendTypewriter
from purdy.content import CodeBlob
from purdy.ui import Screen

screen = Screen()
code_box = screen.code_box
blob = CodeBlob('../display_code/console.py', 'con')
action = AppendTypewriter(code_box, blob)
screen.run([action])