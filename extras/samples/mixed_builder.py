#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates movie mode and the StopMovie action interrupting it
from builder import ActionsBuilder
from purdy.settings import settings
from purdy.ui import SplitScreen

settings["movie_mode"] = 500

py_code = "../display_code/code.py"
con_code = "../display_code/simple.repl"

screen = SplitScreen(settings, top_starting_line_number=-1, top_auto_scroll=False)

actions = (
    ActionsBuilder(screen, "con")
    .append(py_code)
    .wait()
    .switch_to_code_box(1)
    .append_typewriter(con_code)
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
