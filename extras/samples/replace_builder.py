#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates replacing the code in a code box by clearing it and appending
# new code
from purdy.builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=10)
simple = "../display_code/simple.repl"
traceback = "../display_code/traceback.repl"

actions = ActionsBuilder(screen, "con").append(simple).wait().clear().append(traceback)

if __name__ == "__main__":
    screen.run(actions)
