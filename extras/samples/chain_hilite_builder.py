#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates highlight chain action
from builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=1)

actions = (
    ActionsBuilder(screen, "py3")
    .append("../display_code/code.py")
    .highlight_chain(["1-2", "3-4", "5-6", "7-8", "9-12"])
)

if __name__ == "__main__":
    screen.run(actions)
