#!/usr/bin/env python
# box.py
from purdy.tui import AppFactory, BoxSpec, Code, RowSpec, TText

# =============================================================================

CONTENT = """This is some babbling text which will appear in a bunch of different colours. I'll just keep typing for a while. That should be enough I would think, yes?  """

def a1():
    row_specs = [
        RowSpec(1, [BoxSpec(1, border="br"), BoxSpec(2, border="b")]),
        RowSpec(2, [BoxSpec(2), BoxSpec(1)]),
    ]

    app = AppFactory.full(row_specs)
    app.rows[0][0].append(TText("[blue]" + 3 * CONTENT + "[/]"))
    app.rows[0][1].append(TText("[green]" + 5 * CONTENT + "[/]"))
    app.rows[1][0].append(TText("[red]" + 7 * CONTENT + "[/]"))
    app.rows[1][1].append(TText("[orange]" + 7 * CONTENT + "[/]"))
    return app

def a2():
    app = AppFactory.simple()
    app.box.append(TText("[blue]" + 7 * CONTENT + "[/]"))
    return app

def a3():
    app = AppFactory.split(20, relative_height_top=3)
    app.top.append(TText("[blue]" + 7 * CONTENT + "[/]"))
    app.bottom.append(TText("[red]" + 7 * CONTENT + "[/]"))
    return app

a1().run()
#a2().run()
#a3().run()
