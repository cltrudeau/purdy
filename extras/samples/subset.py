#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates a split screen with a large top window

from purdy.actions import (Append, AppendTypewriter, Highlight, StopMovie,
    Wait)
from purdy.content import Code
from purdy.settings import settings
from purdy.ui import SplitScreen

settings['movie_mode'] = 2

original = Code('../display_code/code.py')
code1 = original.subset(3, 18)
code2 = original.subset(28, 39)

screen = SplitScreen(settings, top_height=15)

actions = [
    Append(screen.top, code1),
    Append(screen.bottom, code2),
]

if __name__ == '__main__':
    screen.run(actions)
