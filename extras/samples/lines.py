#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import (AppendAll, Wait, AppendLine, ReplaceLine,
    AppendLineTypewriter, ReplaceLineTypewriter)
from purdy.content import Code
from purdy.ui import Screen

start_code = """\
>>> a = 1
>>> b = 2
>>> c = 3
"""

start = Code(start_code, 'con')

screen = Screen(show_line_numbers=True)
code_box = screen.code_box

actions = [
    AppendAll(code_box, start),
    Wait(),
    AppendLine(code_box, 2, '9', 'con'),
    Wait(),
    ReplaceLine(code_box, 3, '>>> d = 4', 'con'),
    Wait(),
    AppendLineTypewriter(code_box, 1, '56789', 'con'),
    Wait(),
    AppendLineTypewriter(code_box, 1, '333', 'con'),
    AppendLineTypewriter(code_box, 1, '444', 'con'),
    Wait(),
    ReplaceLineTypewriter(code_box, 2, '>>> e = 5', 'con'),
    Wait(),
]

screen.run(actions)
