#!/usr/bin/env python
# tuicon.py
#
# Shows off the main features of the purdy coding interface
from purdy.tui import AppFactory, Code

# =============================================================================

app = AppFactory.simple(auto_scroll=True)
box = app.box

INTRO = """\
[on blue]Demonstrates TUI highlighting embedded in an output file[/]

Press right arrow to continue →
"""

con = Code("../display_code/utest.tuicon")

# Intro
(box
    .append(INTRO)
    .wait()
    .typewriter(con)
    .wait()
    .highlight_chain(3, "3:11,4")
)

app.run()
