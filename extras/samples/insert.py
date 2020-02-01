#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import AppendAll, Insert, Wait, InsertTypewriter
from purdy.content import CodeFile, Code
from purdy.ui import Screen

screen = Screen(show_line_numbers=True)
code_box = screen.code_box
blob = CodeFile('../display_code/code.py', 'py3')

insert_me = """\
        for x in range(1, 3):
           print(x)
"""
blob2 = Code(insert_me, 'py3')

insert_me = """\
        l1 = [5, 6, 7, 8, 9, ]
        l2 = [3, 1, 4, 5, ]
"""
blob3 = Code(insert_me, 'py3')

actions = [
    AppendAll(code_box, blob),
    Wait(),
    Insert(code_box, 6, blob2),
    Wait(),
    InsertTypewriter(code_box, 6, blob3),
]

screen.run(actions)
