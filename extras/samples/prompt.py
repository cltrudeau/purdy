#!/usr/bin/env python

### Example purdy library code
#
# Appends the same colourized Python REPL session to the screen multiple
# times, waiting for a keypress between each

from purdy.actions import Append, AppendPrompt, Wait, SuffixTypewriter
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code_box = screen.code_box

text = """\
# A program with prompts
$ my_program
"""

code = Code(text=text, lexer_name="bash")

actions = [
    Append(code_box, code),
    Wait(),
    SuffixTypewriter(code_box, -1, " foo"),
    Wait(),
    AppendPrompt(code_box, Code(text="Name: ", lexer_name="bash"), "Bob"),
    Wait(),
    AppendPrompt(code_box, Code(text="Number: ", lexer_name="bash"), "42"),
]

if __name__ == '__main__':
    screen.run(actions)
