#!/usr/bin/env python
from rich.color import Color
from rich.segment import Segments
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.scrollbar import ScrollBarRender
from textual.widget import Widget
from textual.widgets import Button, Static

from vscroll import VScrollRender

SAMPLE = """\
[b]# This is a comment line that is supposed to be very long, it should keep going so that we can test what wrapping looks like in a Static box, that almost should be enough[/b]
[i]This is the line after the long line[/i]

And now for some extra text
1
2
3
4
5
6
7
8
9
10
"""

SAMPLE2 = """\
[b]# 2 This is a comment line that is supposed to be very long, it should keep going so that we can test what wrapping looks like in a Static box, that almost should be enough[/b]
"""

class FStatic(Static):
    def __init__(
        self,
        content,
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(content, expand=expand, shrink=shrink, markup=markup,
            name=name, id=id, classes=classes, disabled=disabled)
        self.can_focus = True

#    def on_focus(self, event):
#        self.styles.border = ("solid", "blue")
#
#    def on_blur(self, event):
#        self.styles.border = ("solid", "green")


class Dialog(ModalScreen):
    def __init__(self, text):
        self.text = text
        super().__init__()

    def compose(self):
        with Vertical(id="dialog_box"):
            yield Static(self.text, id="dialog_text")
            yield Button("Ok", id="dialog_ok")

    @on(Button.Pressed, "#dialog_ok")
    def on_button_pressed(self):
        self.app.pop_screen()


class ThinBarRender(ScrollBarRender):
    @classmethod
    def render_bar(cls, size, virtual_size, window_size, position,
            thickness, vertical, back_color, bar_color) -> Segments:
        # Hard code the thickness
        # and colour for now
        return super().render_bar(size, virtual_size, window_size,
            position, 1, vertical, back_color, Color.parse("yellow"))



class CodeBox(Widget):
    def __init__(self, content, id: str):
        self.content = content
        super().__init__(id=id, classes="box")
#        self.can_focus = True

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="vscroller"):
            yield Static(self.content, id="One")

    def on_mount(self):
        for widget in self.query(".vscroller"):
            widget.vertical_scrollbar.renderer = ThinBarRender


class GridLayoutExample(App):
    CSS_PATH = "g.tcss"

    def compose(self) -> ComposeResult:
        with Grid():
            yield CodeBox("[blue][b]One[/blue][/b]\n" + SAMPLE, id="One")
            yield CodeBox("[blue][b]Two[/blue][/b]\n" + SAMPLE2, id="Two")
            yield CodeBox("Three\nPoint Five", id="Three")
            yield CodeBox("Four", id="Four")

    def on_mount(self):
        self.query_one("#Four").tooltip = "Some tool tip text"

        for widget in self.query(".vscroller"):
            widget.vertical_scrollbar.renderer = VScrollRender

        self.set_focus(self.query_one("#One"))

    def on_key(self, event):
        key = event.key
        if key == "plus":
            grid = self.query_one(Grid)
            print(50*"=")
            print("Grid: ", grid)
            print("   ", grid.styles.grid_rows)
            print("   ", dir(grid.styles.grid_rows[0]))
            grid.styles.grid_rows = (
                grid.styles.grid_rows[0].value + 1,
                grid.styles.grid_rows[1]
            )
        elif key == "q":
            exit()
        elif key == "d":
            self.push_screen(Dialog("This is my message. It contains a bunch of text, man do I hate CSS. I'll just keep typing things to see what happens with the wrapping"))


if __name__ == "__main__":
    app = GridLayoutExample()
    app.run()
