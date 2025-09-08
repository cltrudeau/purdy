# features.py
#
# Shows off the main features of the purdy coding interface

from purdy.content import Code
from purdy.tui.codebox import TText
from purdy.tui.apps import split

# =============================================================================

app = split(relative_height_bottom=2, auto_scroll_top=True)
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
repl = Code("../display_code/short.repl")
code = Code("../display_code/short.py")

(top
    .append(TText(INTRO))
    .wait()
    .append("\nThe left arrow allows you to back up ←")
    .wait()
    .append("\n\nPurdy lets you present like you're coding")
    .append("\n   Both in the shell →")
    .wait()
)

(bottom
    .append(con)
    .wait()
)

(top
    .append("\n   and the REPL →")
    .wait()
)

(bottom
    .append(repl)
    .wait()
)

(top
    .append("\n\nThere are a variety of transition animations →")
    .wait()
)

(bottom
    .transition(code)
    .wait()
)

(top
    .append("\n\nYou can highlighting a line of code →")
    .wait()
)

(bottom
    .highlight(0)
    .wait()
)

(top
    .append("\nOr just parts of it →")
    .wait()
)

(bottom
    .highlight_off(0)
    .highlight("1:4,18")
    .wait()
    .highlight_all_off()
    .wait()
)

app.run()
