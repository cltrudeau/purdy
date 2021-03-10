#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates a split screen with content that exceeds the window size
from purdy.builder import ActionsBuilder
from purdy.ui import SplitScreen

screen = SplitScreen(max_height=30)

actions = (
    ActionsBuilder(screen, "con")
    .append("../display_code/console.repl")
    .switch_to_code_box(1)
    .append("../display_code/console.repl")
)

if __name__ == "__main__":
    screen.run(actions)
