#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the use of a custom lexer

from purdy.actions import Append
from purdy.content import Code
from purdy.parser import LexerHolder
from purdy.ui import SimpleScreen

from pygments.lexers.javascript import JavascriptLexer

screen = SimpleScreen()
code_box = screen.code_box

lexer_holder = LexerHolder('js', JavascriptLexer(), 'Javascript', False)
blob = Code('../display_code/ugly.js', lexer_name='custom',
    lexer_holder=lexer_holder)

actions = [
    Append(code_box, blob),
]

if __name__ == '__main__':
    screen.run(actions)
