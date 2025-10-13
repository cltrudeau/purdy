#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates auto scroll when the new line is at the bottom and the text
# wraps. Not so much a demo as a bug test

from purdy.actions import AppendTypewriter, Wait
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
box = screen.code_box

blob = Code(text="""\
>>> print(foo)
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
a bunch of text to fill the screen
>>> print("This is a long string that just goes on and on and should cause the line to wrap. I mean it, it just keeps going, man who types this much?")
This is a long string that just goes on and on and should cause the line to wrap. I mean it, it just keeps going, man who types this much?
""", lexer_name="con")

actions = [
    AppendTypewriter(box, blob),
]

if __name__ == '__main__':
    screen.run(actions)
