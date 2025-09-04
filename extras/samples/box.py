# box.py
from purdy.content import Code
from purdy.tui.apps import app_factory, BoxSpec, RowSpec, simple, split

# =============================================================================

CONTENT = """This is some babbling text which will appear in a bunch of different colours. I'll just keep typing for a while. That should be enough I would think, yes?  """

def a1():
    row_specs = [
        RowSpec(1, [BoxSpec(1, border="br"), BoxSpec(2, border="b")]),
        RowSpec(2, [BoxSpec(2), BoxSpec(1)]),
    ]

    app = app_factory(row_specs)
    app.rows[0][0].content = "[blue]" + 3 * CONTENT + "[/]"
    app.rows[0][1].content = "[green]" + 5 * CONTENT + "[/]"
    app.rows[1][0].content = "[red]" + 7 * CONTENT + "[/]"
    app.rows[1][1].content = "[orange]" + 7 * CONTENT + "[/]"
    return app

def a2():
    app = simple()
    app.box.content = "[blue]" + 7 * CONTENT + "[/]"
    return app

def a3():
    app = split(20, relative_height_top=3)
    app.top.content = "[blue]" + 7 * CONTENT + "[/]"
    app.bottom.content = "[red]" + 7 * CONTENT + "[/]"
    return app

a1().run()
