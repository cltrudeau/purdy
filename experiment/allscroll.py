#!/usr/bin/env python
from textual.app import App, ComposeResult
from textual.containers import Grid, VerticalScroll
from textual.widgets import Static

SAMPLE = """A tail of a hero and her dog that worked in a yard not far from Harvard and this was probably enough text
"""

class GridApp(App):
    CSS_PATH = "allscroll.tcss"
#    DEFAULT_CSS = """
#        Grid {
#            grid-size: 3 1;
#        }
#
#        #vs1 {
#            overflow-y: auto;
#        }
#
#        #vs2 {
#            overflow-y: hidden;
#        }
#
#        #vs3 {
#            overflow-y: scroll;
#        }
#    """

    def compose(self) -> ComposeResult:
        with Grid():
            with VerticalScroll(id="vs1"):
                yield Static("[blue]" + 30 * SAMPLE + "[/]")
            with VerticalScroll(id="vs2"):
                yield Static("[green]" + 30 * SAMPLE + "[/]")
            with VerticalScroll(id="vs3"):
                yield Static("[red]Very little text[/]")


if __name__ == "__main__":
    app = GridApp()
    app.run()
