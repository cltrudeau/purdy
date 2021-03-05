#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates a split screen with three code boxes
from builder import ActionsBuilder
from purdy.ui import Screen, CodeBox

py_code = "../display_code/code.py"
con_code = "../display_code/simple.repl"

screen = Screen(
    rows=[
        CodeBox(starting_line_number=1),
        CodeBox(height=7),
        CodeBox(auto_scroll=False),
    ]
)

actions = (
    ActionsBuilder(screen, "py3")
    .append(py_code)
    .switch_to_code_box(1)
    .append(con_code)
    .switch_to_code_box(2)
    .append(py_code)
)

if __name__ == "__main__":
    screen.run(actions)
