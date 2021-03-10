#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates a split screen with a large top window
from purdy.builder import ActionsBuilder
from purdy.settings import settings
from purdy.ui import SplitScreen

settings["movie_mode"] = 2

py_code = "../display_code/code.py"
con_code = "../display_code/simple.repl"

screen = SplitScreen(settings, top_starting_line_number=10, top_height=35)

actions = (
    ActionsBuilder(screen, "con")
    .append(filename=py_code)
    .wait()
    .switch_to_code_box(1)
    .append_typewriter(filename=con_code)
    .wait()
    .stop_movie()
    .wait()
    .switch_to_code_box(0)
    .highlight(4, True)
    .wait()
    .switch_to_code_box(1)
    .highlight(3, True)
    .wait()
    .switch_to_code_box(0)
    .highlight(4, False)
)

if __name__ == "__main__":
    screen.run(actions)
