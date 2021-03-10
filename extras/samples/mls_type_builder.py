#!/usr/bin/env python

### Example purdy library code
#
# Example of a multi-line string in a Python REPL session using the typewriter
# animation.
from purdy.builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code = "../display_code/mls.repl"

actions = ActionsBuilder(screen, "con").append_typewriter(code).append_typewriter(code)

if __name__ == "__main__":
    screen.run(actions)
