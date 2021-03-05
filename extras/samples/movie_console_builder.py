#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates movie mode
from builder import ActionsBuilder
from purdy.settings import settings
from purdy.ui import SimpleScreen

settings["movie_mode"] = 200

screen = SimpleScreen(settings)
code = "../display_code/console.repl"

actions = ActionsBuilder(screen, "con").append_typewriter(code)

if __name__ == "__main__":
    screen.run(actions)
