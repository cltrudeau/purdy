#!/usr/bin/env python

from purdy.actions import (Append, AppendTypewriter, Wait, Highlight,
    HighlightChain, Transition, Suffix, SuffixTypewriter, Fold)
from purdy.content import Code
from purdy.parser import PurdyLexer
from purdy.ui import Screen, SplitScreen, SimpleScreen, TwinCodeBox, CodeBox

screen = SplitScreen(top_height=30, top_auto_scroll=False,
    compact=True, top_starting_line_number=1)
top = screen.code_boxes[0]
bottom = screen.code_boxes[1]

actions = []

code = Code(f'../display_code/code.py')
con = Code(f'../display_code/console.repl')

actions.extend([
    Append(top, code),
    Append(bottom, con),
    HighlightChain(top, ["19-20"])
])

# --------------------------------------------------------------------------

screen.run(actions)
