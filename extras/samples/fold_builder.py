#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the code folding mechanism
from purdy.builder import ActionsBuilder
from purdy.ui import SimpleScreen


screen = SimpleScreen(starting_line_number=1)
code = "../display_code/code.py"

actions = (
    ActionsBuilder(screen, "py3")
    .append(code)
    .wait()
    .fold(20, 23)
    .wait()
    .fold(27)
    .wait()
    .clear()
    .append(code)
    .fold(2)
)

if __name__ == "__main__":
    screen.run(actions)
