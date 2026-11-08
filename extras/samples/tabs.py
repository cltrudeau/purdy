#!/usr/bin/env python
"""Display tab-separated REPL output at four-column tab stops."""

from purdy.tui import AppFactory, Code

app = AppFactory.simple()
app.box.append(Code.text(
    ">>> print('id\\tscore\\n1\\t42')\n"
    "id\tscore\n"
    "1\t42\n",
    "repl",
))

# The second column starts in column 5 on both output lines.
if __name__ == "__main__":
    app.run()
