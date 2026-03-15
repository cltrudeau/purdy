#!/usr/bin/env python
# spawn.py
from purdy.tui import AppFactory, Code

# =============================================================================

app = AppFactory.split(line_number_bottom=1, auto_scroll_bottom=True)
top = app.top
btm = app.bottom

INTRO = """\
[on blue]Test that line numbers etc stay after a transition[/]

Press right arrow to continue →
"""

code1 = Code.text("import random\nrandom.ranint(3)\n")
code2 = Code.text("print('hello')\n")

(top
    .append(INTRO)
    .wait()
)

(btm
    .append(code1)
    .wait()
    .transition(code2)
)

app.run()
