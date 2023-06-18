#!/usr/bin/env python

### Example purdy library code
#
# Builds a screen with three code boxes: a pair over a third

from purdy.tui.screen import Screen, CodeBox
from purdy.content import Code

left = CodeBox(starting_line_number=10, height=10, width_ratio=0.75)
right = CodeBox(auto_scroll=False)
bottom = CodeBox()
rows = [
    (left, right),
    bottom
]

screen = Screen(rows)

code = Code("../display_code/code.py")
left.actions.append(code)

docstring = Code("../display_code/docstring.py")
right.actions.append(docstring)

yaml = Code("../display_code/hell.yml")
bottom.actions.append(yaml)

screen.run()
