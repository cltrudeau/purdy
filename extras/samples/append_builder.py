#!/usr/bin/env python

### Example purdy library code
#
# Appends the same colourized Python REPL session to the screen multiple
# times, waiting for a keypress between each
from builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=1)
code_box = screen.code_box
code_file = "../display_code/simple.repl"

actions = (
    ActionsBuilder(screen, "bash")
    .append(code_file)
    .wait()
    .append(code_file)
    .wait()
    .append(code_file)
    .wait()
    .append(code_file)
    .wait()
    .append(code_file)
    .wait()
    .append(code_file)
    .wait()
    .append(code_file)
    .wait()
    .append(code_file)
    .wait()
    .append(code_file)
    .wait()
    .append(code_file)
    .wait()
)


if __name__ == "__main__":
    screen.run(actions)
