#!/usr/bin/env python
# features.py
#
# Shows off the main features of the purdy coding interface
from purdy.tui import AppFactory, Code, EscapeText

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
code = Code("../display_code/short.py")
long_code = Code("../display_code/code.py")

# Intro
(top
    .append(INTRO)
    .wait()
)

(top
    .append("The left arrow allows you to back up ←")
    .wait()
    .append("\nPurdy lets you present like you're coding")
    .append("   Both in the shell →")
    .wait()
)

# Bash + REPL
(bottom
    .append(con)
    .wait()
)

(top
    .append("   and the REPL →")
    .wait()
)

(bottom
    .append(repl)
    .wait()
)

# Transition to code
(top
    .append("\nThere are a variety of transition animations →")
    .wait()
)

(bottom
    .transition(code)
    .wait()
)

# Highlights
(top
    .append("\nYou can highlighting a line of code →")
    .wait()
)

(bottom
    .highlight(0)
    .wait()
)

(top
    .append("Or just parts of it →")
    .wait()
)

(bottom
    .highlight_off(0)
    .highlight("1:4,18")
    .wait()
    .highlight_all_off()
    .wait()
)

# Typewriter
(top
    .append("\nYou can emulate typing → → →")
    .wait()
)

(bottom
    .transition()
    .append(con)
    .typewriter(repl)
    .wait()
)

(top
    .append("Typing with Textual markup →")
    .wait()
)

(bottom
    .transition()
    .text_typewriter("one [green]two[/] three")
    .wait()
)

(top
    .append("Or you can escape text to keep it plain →")
    .wait()
)

(bottom
    .text_typewriter(EscapeText("four [five] six"))
    .wait()
)

(top
    .append("You can control the display →")
    .wait()
)

(bottom
    .transition(long_code)
    .wait()
)

(top
    .append("Turn line numbers on →")
    .wait()
)

(bottom
    .set_numbers(1)
    .wait()
)

(top
    .append("Animate scrolling →")
    .wait()
)

(bottom
    .move_by(10)
    .wait()
)

app.run()
