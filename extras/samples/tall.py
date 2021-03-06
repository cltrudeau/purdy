#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates a split screen with a large top window

from purdy.actions import (Append, AppendTypewriter, Highlight, StopMovie,
    Wait)
from purdy.content import Code
from purdy.settings import settings
from purdy.ui import SplitScreen

settings['movie_mode'] = 2

py_code = Code('../display_code/code.py')
con_code = Code('../display_code/simple.repl')

screen = SplitScreen(settings, top_starting_line_number=10, top_height=35)
py_box = screen.top
con_box = screen.bottom

actions = [
    Append(py_box, py_code),
    Wait(),
    AppendTypewriter(con_box, con_code),
    Wait(),
    StopMovie(),
    Wait(),
    Highlight(py_box, 4, True),
    Wait(),
    Highlight(con_box, 3, True),
    Wait(),
    Highlight(py_box, 4, False),
]

if __name__ == '__main__':
    screen.run(actions)
