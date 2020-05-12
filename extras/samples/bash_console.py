#!/usr/bin/env python

### Example purdy library code
#
# Uses the typewriter animation to display a bash console session

from purdy.actions import AppendTypewriter
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code_box = screen.code_box
blob = Code('../display_code/curl.bash')
actions = [
    AppendTypewriter(code_box, blob),
]

if __name__ == '__main__':
    screen.run(actions)
