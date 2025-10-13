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
    PAUSE = 0.05

    async def fill_worker(self):
        line = Static("")
        line.styles.width = "100%"
        line.styles.position = "absolute"
        line.styles.offset = (0, 0)
        line.styles.background = "black 0%"

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

        contents = []
        for count in range(self.app.size.height):
            # Generate a new line
            output = ""
            for trail in trails:
                output += trail.get_content(self.app.size.height, False)

            contents.insert(0, output)
            line.update("\n".join(contents))
            if count == 0:
                self.mount(line)

            await asyncio.sleep(self.PAUSE)

        # Stop generating new char sets
        longest = max([t.length - t.current for t in trails])

        # Loop longest trail length past the terminal height so everything
        # gets pushed down
        for count in range(self.app.size.height + longest):
            contents = contents[0:-1]

            # Generate a new line
            output = ""
            for trail in trails:
                output += trail.get_content(self.app.size.height, True)

            contents.insert(0, output)
            line.update("\n".join(contents))

            await asyncio.sleep(self.PAUSE)

        # Clean-up in case we're called again
        line.remove()
        self.app.pop_screen()

    async def on_screen_resume(self):
        self.run_worker(self.fill_worker(), exclusive=True)


class CurtainScreen(FunkyScreen):
    PAUSE = 0.02

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
            await asyncio.sleep(self.PAUSE)

        for count in range(self.app.size.height):
            curtain.styles.height = self.app.size.height - count
            curtain.styles.offset = (0, count)
            await asyncio.sleep(self.PAUSE)

        curtain.styles.visibility = "hidden"
        self.app.pop_screen()

    async def on_screen_resume(self):
        self.run_worker(self.fill_worker(), exclusive=True)


class FireScreen(Screen):
    """Fire effects adapted from Asciimatics:

    https://github.com/peterbrittain/asciimatics

    Who adapted it from Hugo Elias:

    https://web.archive.org/web/20160418004150/http://freespace.virgin.net/hugo.elias/models/m_fire.htm

    Basic concept: a list-of-lists is used as a buffer with pixel intensity
    values. Fire animation randomly cools some of the spots as well as
    convects the pixels upwards. After random cooling, a smoothing function is
    run average the heat value of each pixel based on the four around it.

    To start, the fire is a single line at the bottom of the screen made up of
    a random number of pixels based on cls.INTENSITY. Each time convection
    happens a new row is inserted and the top-most one is cycled out.

    The Label isn't based on the whole buffer, any empty lines at the top
    aren't included to keep transparency happening until the burn has consumed
    the whole screen.
    """

    DEFAULT_CSS = """
        FireScreen {
            background: black 0%;
            align: left bottom;
        }
    """

    PAUSE = 0.005       # wait time between frames
    SPOT = 60           # how hot the emitter values are
    INTENSITY = 0.80    # random chance for a new emitter
    FRAMES_AFTER_CONSUMPTION = 20      # how long after filling screen to go
    PERCENTAGE_COOLING_SPOTS = 0.02    # percentage of pixels that get cooled
    COLOURS = [
        "#000000",
        "#5F0000",
        "#870000",
        "#AF0000",
        "#D70000",
        "#FF0000",
        "#FF5F00",
        "#FF8700",
        "#FFAF00",
        "#FFD700",
        "#FFFF00",
        "#FFFF5F",
        "#FFFF87",
        "#FFFFAF",
        "#FFFFD7",
        "#FFFFFF",
    ]

    def convert_pixels(self, max_height=1):
        # Converts the internal list-of-lists buffer with the heat values into
        # a string that can be used by a Label
        content = ""

        content = ""
        for count, pixels in enumerate(self.pixel_lines):
            fire_height = count + 1
            line = ""
            for pixel in pixels:
                index = min(len(self.COLOURS) - 1, pixel)
                if index < 0:
                    index = 0

                line += f"[on {self.COLOURS[index]}] [/]"

            if count == 0:
                content = line
            else:
                content = line + "\n" + content

            if fire_height >= max_height:
                # We've hit the maximum allowed height, stop generating text
                break

        return content

    def emitter_line(self, width, extinguish=0):
        # Generate a new line of heat values
        line = []
        for _ in range(width):
            if random() < self.INTENSITY - extinguish:
                line.append(randint(1, self.SPOT))
            else:
                line.append(0)

        return line

    async def animate_fire(self, duration, growth=True, extinguish=0):
        for frame in range(duration):
            # Convection pushes everything up, sticking a new emitter at the
            # bottom (pixel array is upside down)
            self.pixel_lines.insert(0, self.emitter_line(self.width,
                frame * extinguish))
            del self.pixel_lines[-1]

            # Seed some random cooling spots
            num_spots = (frame * self.width * self.PERCENTAGE_COOLING_SPOTS)
            for _ in range(int(num_spots)):
                row = randint(0, self.height - 1)
                col = randint(0, self.width - 1)
                self.pixel_lines[row][col] -= 10

            # Simulate cooling by averaging surrounding pixels
            for row in range(self.height):
                for col in range(self.width):
                    values = []
                    # To the right
                    if col + 1 < self.width:
                        values.append(self.pixel_lines[row][col + 1])
                    # To the left
                    if col - 1 > 0:
                        values.append(self.pixel_lines[row][col - 1])
                    # Above
                    if row + 1 < self.height:
                        values.append(self.pixel_lines[row + 1][col])
                    # Below
                    if row - 1 > 0:
                        values.append(self.pixel_lines[row - 1][col])

                    # Average the values
                    self.pixel_lines[row][col] = int(mean(values))

            max_height = self.height
            if growth:
                max_height = min(self.height, frame)

            content = self.convert_pixels(max_height)
            self.label.update(content)
            await asyncio.sleep(self.PAUSE)


    async def fill_worker(self):
        self.width = self.app.size.width
        self.height = self.app.size.height
        self.label = Label("")
        self.label.width = "100%"

        # Create a pixel buffer the size of the screen with zero values, then
        # stick an emitter line at the bottom of it
        self.pixel_lines = [
            [0 for _ in range(self.width)] for _ in range(self.height - 1)
        ]
        self.pixel_lines.insert(0, self.emitter_line(self.width))

        # Generate the display text and show the label
        content = self.convert_pixels()
        self.label.update(content)
        self.mount(self.label)

        await self.animate_fire(self.height)
        await self.animate_fire(self.FRAMES_AFTER_CONSUMPTION, False, 0.08)

        # Clean-up in case we're called again
        self.label.remove()
        self.app.pop_screen()

    async def on_screen_resume(self):
        self.run_worker(self.fill_worker(), exclusive=True)


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
