#!/usr/bin/env python
# mixed.py
from purdy.tui import AppFactory, Code

# =============================================================================

app = AppFactory.simple(auto_scroll=True)
box = app.box

text = """\
$ python
Python 3.13.5 (v3.13.5:6cb20a219a8, Jun 11 2025, 12:23:45)
Type "help", "copyright", "credits" or "license" for more information.
"""

con = Code.text(text)
repl = Code("../display_code/console.repl", theme="pyrepl")
code = Code("../display_code/code.py")

(box
#    .append(con)
#    .typewriter(repl)
#    .wait()
#    .transition(code[0:3])
    .append(code[0:3])
    .wait()
    .highlight_chain(0, "1:4,10", 2, [0, "1:0,3"], "1:arg:1")
#    .highlight_chain("1:4,10", "1:arg:0", "1:arg:1")
    .wait()
    .set_numbers(1)
    .wait()
    .append(code[3:])
)

app.run()
