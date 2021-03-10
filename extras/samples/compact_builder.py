#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the use of compact dividers
from purdy.builder import ActionsBuilder
from purdy.ui import SplitScreen

screen = SplitScreen(compact=True)

code = "../display_code/console.repl"
actions = ActionsBuilder(screen, "con").append(code).switch_to_code_box(1).append(code)

if __name__ == "__main__":
    screen.run(actions)
