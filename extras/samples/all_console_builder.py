#!/usr/bin/env python

### Example purdy library code
#
# Displays a colourized Python REPL session to the screen
from purdy.builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen()
actions = ActionsBuilder(screen, "con").append("../display_code/console.repl")

if __name__ == "__main__":
    screen.run(actions)
