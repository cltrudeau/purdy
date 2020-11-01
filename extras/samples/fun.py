#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the RunFunction action

from purdy.actions import Append, Wait, RunFunction
from purdy.content import Code
from purdy.ui import SimpleScreen

def do_something(foo, bar=3):
    with open('zzz_output.txt', 'a') as f:
        f.write(f'Doing something {foo} {bar}\n')


def undo_something(foo, bar=3):
    with open('zzz_output.txt', 'a') as f:
        f.write(f'Undoing something {foo} {bar}\n')


screen = SimpleScreen(starting_line_number=10)
code_box = screen.code_box
first = Code(text="First things first")
second = Code(text="Second things second")
third = Code(text="Now read zzz_output.txt file to check it worked")

actions = [
    Append(code_box, first),
    Wait(),
    RunFunction(do_something, undo_something, 'FOO', bar=42),
    Wait(),
    Append(code_box, second),
    Wait(),
    Append(code_box, third),
]

if __name__ == '__main__':
    screen.run(actions)
