#!/usr/bin/env python

# Example code for showing a top with code and a bottom with console

from purdy.actions import AppendAll, AppendTypewriter, Highlight, StopMovie
from purdy.content import CodeFile
from purdy.settings import settings
from purdy.ui import SplitScreen

settings['movie_mode'] = 2

py_code = CodeFile('../display_code/code.py', 'py3')
con_code = CodeFile('../display_code/simple.py', 'con')

screen = SplitScreen(settings, show_top_line_numbers=True)
py_box = screen.top_box
con_box = screen.bottom_box

actions = [
    AppendAll(py_box, py_code),
    AppendTypewriter(con_box, con_code),
    StopMovie(screen),
    Highlight(py_box, 3, True),
    Highlight(con_box, 3, True),
    Highlight(py_box, 3, False),
]

screen.run(actions)
