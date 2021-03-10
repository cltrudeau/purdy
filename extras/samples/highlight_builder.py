#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates highlighting and unhighlighting lines of code
from purdy.builder import ActionsBuilder
from purdy.settings import settings
from purdy.ui import SimpleScreen

screen = SimpleScreen(settings, starting_line_number=1)
code = "../display_code/console.repl"

actions = (
    ActionsBuilder(screen, "bash")
    .append(code)
    .wait()
    .highlight(range(5, 41), True)
    .wait()
    .highlight("5,6,10-20", False)
)

if __name__ == "__main__":
    screen.run(actions)
