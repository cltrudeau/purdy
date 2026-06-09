#!/usr/bin/env python
# features.py
#
# Shows off the main features of the purdy coding interface
from purdy.tui import AppFactory, Code, EscapeText, TextSection

# =============================================================================

app = AppFactory.simple(auto_scroll=True, max_height=10)
box = app.box

con = Code("../display_code/count.con")

# Intro
(box
    .typewriter(con, more=10)
)

app.run()
