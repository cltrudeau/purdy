#!/usr/bin/env python
import asyncio
from dataclasses import dataclass
from random import randint, random
from statistics import mean

from rich.color import Color
from rich.segment import Segments
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, VerticalScroll
from textual.markup import escape
from textual.screen import ModalScreen, Screen
from textual.scrollbar import ScrollBarRender
from textual.widget import Widget
from textual.widgets import Button, Static, Label

from vscroll import VScrollRender

SAMPLE = """\
One and a tail of a hero and her dog
Two that worked in a yard
Three not far from Harvard
Four and this was probably enough text
"""

#SAMPLE = """\
#>>> print("foo")
#foo
#"""

SAMPLE2 = """\
>>> print("bar")
bar
"""

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
            yield Static(self.content, id=self.id + "-static")

    def on_mount(self):
        for widget in self.query(".vscroller"):
            widget.vertical_scrollbar.renderer = ThinBarRender


class OverlayScreen(Screen):
    def compose(self):
        yield Static(
            (
                "\n"
                "1   overlay\n"
                "[blue]2 overlay[/blue]"
            ),
            id="overlay-text"
        )


class Floater(Label):
    pass


class GridLayoutExample(App):
    CSS_PATH = "h.tcss"
    SCREENS = {
        "overlay_screen": OverlayScreen,
        "curtain_screen": CurtainScreen,
        "matrix_screen": MatrixScreen,
        "fire_screen": FireScreen,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animating = False

    def compose(self) -> ComposeResult:
        with Grid():
            yield CodeBox(SAMPLE, id="One")
            yield CodeBox("$ ", id="Two")
            yield Floater("this is floating text", id="floater")

    def on_mount(self):
        self.set_focus(self.query_one("#One"))

    async def animate_floater(self):
        floater = self.query_one("#floater")
        floater.styles.visibility = "visible"
        for count in range(self.size.height):
            await asyncio.sleep(0.1)
            floater.styles.offset = (count, count)

        floater.styles.visibility = "hidden"
        floater.styles.offset = (0, 0)

    async def animate_typing(self, content):
        box = self.query_one("#One-static")
        box.update(box._content + "\n")
        for count, letter in enumerate(content):
            await asyncio.sleep(0.2)
            box.update(box._content + letter)

            if not self.animating:
                # Animation was cancelled
                box.update(box._content + content[count + 1:])
                break


    async def stop_all_animations(self, complete):
        for key in list(self._animator._scheduled.keys()):
            await self._animator._stop_scheduled_animation(key, complete)

        for key in list(self._animator._animations.keys()):
            await self._animator._stop_running_animation(key, complete)

    async def on_key(self, event):
        key = event.key
        if key == "q":
            exit()
        elif key == "t":
            self.animating = True
            self.run_worker(
                self.animate_typing("this is a new line being typed"),
                exclusive=True)
        elif key == "c":
            self.animating = False
            print("**** calling stop")
            await self.stop_all_animations(False)
        elif key == "x":
            self.animating = True
            self.run_worker( self.animate_transition(), exclusive=True)
        elif key == "h":
            self.styles.animate("opacity", value=0.0, duration=5.0)
        elif key == "s":
            if self.screen != self.transition_screen:
                self.push_screen("transition_screen")
            else:
                print("**** Not doing it twice")
        elif key == "p":
            self.pop_screen()
        elif key == "o":
            self.push_screen("overlay_screen")
        elif key == "g":
            self.run_worker(self.animate_floater(), exclusive=True)
        elif key in ["1", "2", "3"]:
            if self.screen.id != "_default":
                print("**** Not doing it twice")
            else:
                if key == "1":
                    self.push_screen("curtain_screen")
                elif key == "2":
                    self.push_screen("matrix_screen")
                elif key == "3":
                    self.push_screen("fire_screen")
        elif key == "d":
            print(50*">")

            print("***** query()")
            print(self)
            for widget in self.query():
                print(widget)

            print("***** children")
            def print_kids(node):
                for child in node.children:
                    print(child)
                    print_kids(child)

            print_kids(self)
            print(50*"=")

            print_kids(self.transition_screen)

            print(50*"<")


if __name__ == "__main__":
    app = GridLayoutExample()
    app.run()
