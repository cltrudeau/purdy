#!/usr/bin/env python

### Example purdy library code
#
# Displays a REPL session without any token processing using the "none" lexer,
# highlighting the first three lines in succession

from purdy.actions import Append, Wait, HighlightChain
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code_box = screen.code_box
blob = Code('../display_code/simple.repl', lexer_name="none")

actions = [
    Append(code_box, blob),
    Wait(),
    HighlightChain(code_box, [1, 2, 3]),
]

if __name__ == '__main__':
    screen.run(actions)
