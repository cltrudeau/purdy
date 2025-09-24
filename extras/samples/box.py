#!/usr/bin/env python
# box.py
from purdy.tui import AppFactory, BoxSpec, Code, RowSpec

# =============================================================================

CONTENT = """This is some babbling text which will appear in a bunch of different colours. I'll just keep typing for a while. That should be enough I would think, yes?  """

def a1():
    row_specs = [
        RowSpec(1, [BoxSpec(1, border="br"), BoxSpec(2, border="b")]),
        RowSpec(2, [BoxSpec(2), BoxSpec(1)]),
    ]

    app = AppFactory.full(row_specs)
    app.rows[0][0].append("[blue]" + 3 * CONTENT + "[/]")
    app.rows[0][1].append("[green]" + 5 * CONTENT + "[/]")
    app.rows[1][0].append("[red]" + 7 * CONTENT + "[/]")
    app.rows[1][1].append("[orange]" + 7 * CONTENT + "[/]")
    return app

def a2():
    app = AppFactory.simple(title="[yellow]Static title[/]")
    app.box.append("[blue]" + 7 * CONTENT + "[/]")
    return app

def a3():
    app = AppFactory.split(20, relative_height_top=3,
        top_title="[yellow]Top static title[/]",
        bottom_title="[yellow]Top static title[/]")
    app.top.append("[blue]" + 7 * CONTENT + "[/]")
    app.bottom.append("[red]" + 7 * CONTENT + "[/]")
    return app

#a1().run()
#a2().run()
a3().run()
