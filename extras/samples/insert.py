#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates inserting lines of code with and without typewriter animation

from purdy.actions import Append, Insert, Wait, InsertTypewriter
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=10)
code_box = screen.code_box
blob = Code('../display_code/code.py')

insert_me = """\
        for x in range(1, 3):
           print(x)"""
blob2 = Code(text=insert_me, lexer_name='py3')

insert_me = """\
        l1 = [5, 6, 7, 8, 9, ]
        l2 = [3, 1, 4, 5, ]"""
blob3 = Code(text=insert_me, lexer_name='py3')

insert_me = "        self.stuff(1)"
blob4 = Code(text=insert_me, lexer_name='py3')

actions = [
    Append(code_box, blob),
    Wait(),
    Insert(code_box, 8, blob2),
    Wait(),
    InsertTypewriter(code_box, 8, blob3),
    Insert(code_box, 8, blob4),
]

if __name__ == '__main__':
    screen.run(actions)
