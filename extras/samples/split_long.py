#!/usr/bin/env python

# Example code for showing a top with code and a bottom with console

from purdy.actions import AppendAll
from purdy.content import CodeFile
from purdy.settings import settings
from purdy.ui import SplitScreen

settings['movie_mode'] = 20

code1 = CodeFile('../display_code/console2.py', 'con')
code2 = CodeFile('../display_code/console2.py', 'con')

screen = SplitScreen(settings)
box1 = screen.top_box
box2 = screen.bottom_box

actions = [
    AppendAll(box1, code1),
    AppendAll(box2, code2),
]

screen.run(actions)
