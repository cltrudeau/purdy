#!/usr/bin/env python
# features.py
#
# Shows off the main features of the purdy coding interface
from purdy.tui import AppFactory, Code, TText

# =============================================================================

app = AppFactory.split(relative_height_bottom=2, auto_scroll_top=True)
top = app.top
bottom = app.bottom

INTRO = """\
[on blue]Welcome to the purdy features demo[/]

Press right arrow to show the next animation step →
"""

shell = """\
$ python
Python 3.13.5 (v3.13.5:6cb20a219a8, Jun 11 2025, 12:23:45)
Type "help", "copyright", "credits" or "license" for more information.
"""

con = Code.text(shell, "con")
repl = Code("../display_code/really_short.repl")
#repl = Code("../display_code/short.repl")
code = Code("../display_code/short.py")

## Intro
#(top
#    .append(TText(INTRO))
#    .wait()
#)
#
#(top
#    .append("\nThe left arrow allows you to back up ←")
#    .wait()
#    .append("\n\nPurdy lets you present like you're coding")
#    .append("\n   Both in the shell →")
#    .wait()
#)
#
## Bash + REPL
#(bottom
#    .append(con)
#    .wait()
#)
#
#(top
#    .append("\n   and the REPL →")
#    .wait()
#)
#
#(bottom
#    .append(repl)
#    .wait()
#)
#
## Transition to code
#(top
#    .append("\n\nThere are a variety of transition animations →")
#    .wait()
#)
#
#(bottom
#    .transition(code)
#    .wait()
#)
#
## Highlights
#(top
#    .append("\n\nYou can highlighting a line of code →")
#    .wait()
#)
#
#(bottom
#    .highlight(0)
#    .wait()
#)
#
#(top
#    .append("\nOr just parts of it →")
#    .wait()
#)
#
#(bottom
#    .highlight_off(0)
#    .highlight("1:4,18")
#    .wait()
#    .highlight_all_off()
#    .wait()
#)

# Typewriter
(top
    .append("\n\nYou can emulate typing → → →")
    .wait()
)

(bottom
#    .transition()
    .typewriter(repl)
    .wait()
)

(top
    .append("\nTyping with arbitrary text →")
    .wait()
)

(bottom
    .transition()
    .text_typewriter("one two three [not markup]")
    .wait()
)

(top
    .append("\nAnd Textual markup text →")
    .wait()
)

(bottom
    .text_typewriter(TText("\nfour [green]five[/] six"))
    .wait()
)

app.run()
