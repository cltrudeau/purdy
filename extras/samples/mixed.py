#!/usr/bin/env python

# Example code for showing a top with code and a bottom with console

from pathlib import Path

from purdy.content import CodeBlob
from purdy.actions import AppendAll
from purdy.ui import Screen

blob = CodeBlob('../display_code/console.py', 'con')

screen = Screen()
code_box = screen.code_box

actions = [
    AppendAll(code_box, blob),
]

screen.run(actions)
