#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the Shell action that runs a subprocess and returns the result

from purdy.actions import Shell, AppendTypewriter
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code_box = screen.code_box

cmd1 = 'echo "hello there"'
cmd2 = 'echo "it is a nice day today"'

blob = Code(text=f'$ {cmd1}')
blob2 = Code(text=f'$ {cmd2}')

actions = [
    AppendTypewriter(code_box, blob),
    Shell(code_box, cmd1),
    AppendTypewriter(code_box, blob2),
    Shell(code_box, cmd2),
]

if __name__ == '__main__':
    screen.run(actions)
