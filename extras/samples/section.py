#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the use of sections and skipping to them with "S"
from purdy.builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen()

actions = (
    ActionsBuilder(screen, "con")
    .append(text=">>> 1")
    .wait()
    .append(text=">>> 2")
    .wait()
    .append(text=">>> 3")
    .wait()
    .section()
    .append(text=">>> 10")
    .wait()
    .append(text=">>> 11")
    .wait()
    .section()
    .append(text=">>> 20")
    .wait()
    .append(text=">>> 21")
)

if __name__ == "__main__":
    screen.run(actions)
