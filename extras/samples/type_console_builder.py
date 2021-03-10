#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates typewrite animation with a colourized Python REPL session
from purdy.builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code = "../display_code/console.repl"

actions = ActionsBuilder(screen, "con").append_typewriter(code)

if __name__ == "__main__":
    screen.run(actions)
