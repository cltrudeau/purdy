#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the use of sections and skipping to them with "S"
from purdy.builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen()

actions = (
    ActionsBuilder(screen, "con")
    .append(text=">>> # use 3s to skip ahead 3 steps")
    .append_typewriter(text=">>> 2\n>>> 3\n>>> 4")
    .append(text=">>> # use 2S to skip ahead 2 sections")
    .wait()
    .append_typewriter(text=">>> 10")
    .append_typewriter(text=">>> 11")
    .append_typewriter(text=">>> 12")
    .section()
    .append_typewriter(text=">>> 20")
    .append_typewriter(text=">>> 21")
    .append_typewriter(text=">>> 22")
    .section()
    .append_typewriter(text=">>> 30")
    .append_typewriter(text=">>> 31")
    .append_typewriter(text=">>> 32")
    .section()
    .append(text=">>> # type a number then hit ESC to clear it")
    .append_typewriter(text=">>> 40")
    .append_typewriter(text=">>> 41")
    .append(text=">>> # now try it with backwards")
    .wait()
)

if __name__ == "__main__":
    screen.run(actions)
