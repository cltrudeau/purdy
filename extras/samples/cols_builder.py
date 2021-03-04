#!/usr/bin/env python

### Example purdy library code
#
# Shows a split screen session with two code boxes on top and a third below.
from builder import ActionsBuilder
from purdy.ui import Screen, CodeBox, TwinCodeBox

py_code = "../display_code/code.py"
con_code = "../display_code/console.repl"

screen = Screen(
    rows=[
        TwinCodeBox(left_starting_line_number=1, right_weight=2, height=14),
        CodeBox(auto_scroll=False),
    ]
)

actions = (
    ActionsBuilder(screen, "py3")
    .append(py_code)
    .switch_to_code_box(1)
    .append(con_code)
    .switch_to_code_box(2)
    .append(con_code)
)

if __name__ == "__main__":
    screen.run(actions)
