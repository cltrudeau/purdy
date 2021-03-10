#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the use of a custom lexer
from builder import ActionsBuilder
from purdy.content import Code
from purdy.parser import PurdyLexer
from purdy.ui import SimpleScreen

from pygments.lexers.javascript import JavascriptLexer

screen = SimpleScreen()

lexer = PurdyLexer("js", "Javascript", JavascriptLexer, False, "code")
blob = Code("../display_code/ugly.js", lexer_name="custom", purdy_lexer=lexer)

actions = ActionsBuilder(screen, 'py3').append(code=blob)

if __name__ == "__main__":
    screen.run(actions)
