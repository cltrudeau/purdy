#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the Shell action that runs a subprocess and returns the result
from purdy.builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen()

cmd1 = 'echo "hello there"'
cmd2 = 'echo "it is a nice day today"'

actions = (
    ActionsBuilder(screen, "bash")
    .append_typewriter(text=f"$ {cmd1}")
    .shell(cmd1)
    .append_typewriter(text=f"$ {cmd2}")
    .shell(cmd2)
)

if __name__ == "__main__":
    screen.run(actions)
