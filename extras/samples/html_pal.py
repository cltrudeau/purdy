#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates using the XML colourizing palatte and custom lexer

from purdy.actions import Append, Highlight, Wait
from purdy.content import Code
from purdy.parser import PurdyLexer
from purdy.settings import settings
from purdy.ui import SimpleScreen

from pygments.lexers.html import HtmlLexer

screen = SimpleScreen(settings, starting_line_number=1)
code_box = screen.code_box

lexer = PurdyLexer('html', 'Html', HtmlLexer, False, 'xml')
blob = Code('../display_code/base.html', lexer_name='custom', purdy_lexer=lexer)

actions = [
    Append(code_box, blob),
    Wait(),
    Highlight(code_box, range(5, 41), True),
]

if __name__ == '__main__':
    screen.run(actions)
