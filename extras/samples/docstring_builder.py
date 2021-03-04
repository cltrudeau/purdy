#!/usr/bin/env python

### Example purdy library code
#
# Displays a function with a multi-line doc string (these can be tricky to
# parse, want to make sure each line is colourized as a string)
from builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen()
actions = ActionsBuilder(screen, "py3").append("../display_code/docstring.py")

if __name__ == "__main__":
    screen.run(actions)
