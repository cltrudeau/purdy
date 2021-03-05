#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates removing lines of code
from builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=1)
code = "../display_code/code.py"

actions = (
    ActionsBuilder(screen, "py3")
    .append(code)
    .wait()
    .remove(10, 4)
    .wait()
    .remove(12, 1)
    .wait()
    .remove(15, 3)
)

if __name__ == "__main__":
    screen.run(actions)
