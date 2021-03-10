#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates using the XML colourizing palatte and custom lexer
from purdy.builder import ActionsBuilder
from purdy.content import Code
from purdy.parser import PurdyLexer
from purdy.settings import settings
from purdy.ui import SimpleScreen

from pygments.lexers.html import HtmlLexer

screen = SimpleScreen(settings, starting_line_number=1)

lexer = PurdyLexer("html", "Html", HtmlLexer, False, "xml")
blob = Code(
    "/Users/ctrudeau/s/RealPython/drf/code/Fedora/templates/registration/login.html",
    lexer_name="custom",
    purdy_lexer=lexer,
)

actions = ActionsBuilder(screen, 'py3').append(code=blob).wait().highlight(range(5, 41), True)


if __name__ == "__main__":
    screen.run(actions)
