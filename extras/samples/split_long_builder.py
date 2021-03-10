#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates a split screen with content that exceeds the window size
from purdy.builder import ActionsBuilder
from purdy.ui import SplitScreen

code = "../display_code/console.repl"

screen = SplitScreen()

actions = ActionsBuilder(screen, "con").append(code).switch_to_code_box(1).append(code)

if __name__ == "__main__":
    screen.run(actions)
