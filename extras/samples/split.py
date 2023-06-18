#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the use of the SplitScreen short-cut that creates a top and
# bottom code box

from purdy.tui.screen import SplitScreen
from purdy.content import Code

screen = SplitScreen(bottom_auto_scroll=False, max_height=20)
top = screen.top
bottom = screen.bottom

code = Code("../display_code/code.py")
top.actions.append(code)

yaml = Code("../display_code/hell.yml")
bottom.actions.append(yaml)

screen.run()
#screen.print_steps()
