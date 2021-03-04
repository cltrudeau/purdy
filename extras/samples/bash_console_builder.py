#!/usr/bin/env python

### Example purdy library code
#
# Uses the typewriter animation to display a bash console session
from builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen()
actions = ActionsBuilder(screen, "bash").append_typewriter("../display_code/curl.bash")

if __name__ == "__main__":
    screen.run(actions)
