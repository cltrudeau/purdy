#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from purdy.actions import AppendAll, Insert
from purdy.content import CodeFile, Code
from purdy.ui import Screen

screen = Screen(show_line_numbers=True)
code_box = screen.code_box
blob = CodeFile('../display_code/simple.py', 'con')

insert_me = """\
>>> for x in range(1, 3):
...    print(x)
1
2
"""

blob2 = Code(insert_me, 'con')

actions = [
    AppendAll(code_box, blob),
    Insert(code_box, 4, blob2)
]

screen.run(actions)
