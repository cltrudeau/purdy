#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the Sleep action
from builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=10)
code = "../display_code/simple.repl"

actions = ActionsBuilder(screen, "con").append(code).sleep(3).append(code)

if __name__ == "__main__":
    screen.run(actions)
