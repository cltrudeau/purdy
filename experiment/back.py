#!/usr/bin/env python
import asyncio
from dataclasses import dataclass
from random import randint

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


class FunkyScreen(Screen):
    DEFAULT_CSS = """
        FunkyScreen {
            background: black 0%;
        }
    """


@dataclass
class MatrixTrail:
    length: int
    gap: int
    current: int = 0

    styles = [
        "[lime bold]",
        "[lime]",
        "[limegreen bold]",
        "[limegreen]",
        "[green]",
    ]

    def get_content(self, height, complete):
        if self.gap > 0:
            # Trail is between sets of chars, reduce gap count
            self.gap -= 1
            return " "

        # We're in a char set, move to the next one
        self.current += 1

        if self.current > self.length:
            # End of self, reset it
            self.current = 0
            self.length = randint(3, height // 3)

            if complete:
                # Done creating new sets, make sure nothing but blanks from
                # here on
                self.gap = height * 2
            else:
                self.gap = randint(3, 7)
            return " "

        # else, Print a character for this char set
        letter = randint(32, 126)
        if 91 <= letter <= 93:
            # Markup's special characters ([, / ]), can't use them
            letter += 4

        index = -1 if self.current >= len(MatrixTrail.styles) \
            else self.current - 1
        return f"{self.styles[index]}{chr(letter)}[/]"


class MatrixScreen(FunkyScreen):
    def _create_line(self, content):
        line = Static(content)
        line.styles.width = "100%"
        line.styles.position = "absolute"
        line.styles.offset = (0, 0)
        line.styles.background = "black 0%"
        return line

    async def fill_worker(self):
        trails = []
        space = randint(2, 5)
        for x in range(self.app.size.width):
            letter = randint(32, 126)
            if 91 <= letter <= 93:
                # Markup's special characters, can't use them
                letter += 4

            # Start with random spacing between the beginning of columns
            space -= 1
            if space == 0:
                space = randint(2, 5)
                trail = MatrixTrail(
                    length = randint(3, self.app.size.height // 3),
                    gap = 0,
                )
            else:
                trail = MatrixTrail(
                    length = randint(3, self.app.size.height // 3),
                    gap = randint(1, 7)
                )


            trails.append(trail)

        lines = []

        for _ in range(self.app.size.height):
            # Move everything down one
            for line in lines:
                x = line.styles.offset.x.value
                y = line.styles.offset.y.value
                line.styles.offset = (x, y + 1)

            # Generate a new line
            content = ""
            for trail in trails:
                content += trail.get_content(self.app.size.height, False)

            line = self._create_line(content)
            lines.append(line)
            self.mount(line)

            await asyncio.sleep(0.1)

        # Stop generating new char sets
        longest = max([t.length - t.current for t in trails])

        # Loop longest trail length past the terminal height so everything
        # gets pushed down
        for _ in range(self.app.size.height + longest):
            # Move everything down one
            for line in lines:
                x = line.styles.offset.x.value
                y = line.styles.offset.y.value
                line.styles.offset = (x, y + 1)

            # Generate a new line
            content = ""
            print(trails[:6])
            for trail in trails:
                content += trail.get_content(self.app.size.height, True)

            line = self._create_line(content)
            lines.append(line)
            self.mount(line)
            lines[0].remove()

            await asyncio.sleep(0.1)

        # Clean-up in case we're called again
        for line in lines:
            line.remove()
        self.app.pop_screen()

    async def on_screen_resume(self):
        self.run_worker(self.fill_worker(), exclusive=True)


class CurtainScreen(FunkyScreen):
    def compose(self):
        yield Label("", id="curtain_label")

    async def fill_worker(self):
        curtain = self.query_one("#curtain_label")
        curtain.styles.offset = (0, 0)
        curtain.styles.height = 1
        curtain.styles.width = "100%"
        curtain.styles.background = "yellow"

        curtain.styles.visibility = "visible"

        for count in range(self.app.size.height):
            curtain.styles.height = count
            await asyncio.sleep(0.02)

        for count in range(self.app.size.height):
            curtain.styles.height = self.app.size.height - count
            curtain.styles.offset = (0, count)
            await asyncio.sleep(0.02)

        curtain.styles.visibility = "hidden"
        self.app.pop_screen()

    async def on_screen_resume(self):
        self.run_worker(self.fill_worker(), exclusive=True)


class GridLayoutExample(App):
    CSS_PATH = "h.tcss"
    SCREENS = {
        "overlay_screen": OverlayScreen,
        "curtain_screen": CurtainScreen,
        "matrix_screen": MatrixScreen,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animating = False

    def compose(self) -> ComposeResult:
        yield Floater("this is floating text", id="floater")

        with Grid():
            yield CodeBox(SAMPLE, id="One")
            yield CodeBox("$ ", id="Two")

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
        elif key == "1":
            if self.screen.id == "_default":
                self.push_screen("curtain_screen")
            else:
                print("**** Not doing it twice")
        elif key == "2":
            if self.screen.id == "_default":
                self.push_screen("matrix_screen")
            else:
                print("**** Not doing it twice")
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
