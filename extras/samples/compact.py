#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the use of compact dividers

from purdy.actions import Append
from purdy.content import Code
from purdy.ui import SplitScreen

screen = SplitScreen(compact=True)
top = screen.top
bottom = screen.bottom

blob = Code('../display_code/console.repl')
actions = [
    Append(top, blob),
    Append(bottom, blob),
]

if __name__ == '__main__':
    screen.run(actions)
