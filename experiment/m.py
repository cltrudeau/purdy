#!/usr/bin/env python
from math import ceil

from rich.color import Color
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment, Segments
from rich.style import Style, StyleType

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


class SBR(ScrollBarRender):
    @classmethod
    def render_bar(
        cls,
        size: int = 25,
        virtual_size: float = 50,
        window_size: float = 20,
        position: float = 0,
        thickness: int = 1,
        vertical: bool = True,
        back_color: Color = Color.parse("#555555"),
        bar_color: Color = Color.parse("bright_magenta"),
    ) -> Segments:

        bars = cls.VERTICAL_BARS

        back = back_color
        bar = bar_color

        len_bars = len(bars)

        width_thickness = 1

        blank = cls.BLANK_GLYPH * width_thickness
        white = Color.parse("white")

        bg_segment = Segment(blank, Style(bgcolor=back))
        segments = [bg_segment] * int(size)
        segments[0] = Segment("▲", Style(color=white))
        segments[-1] = Segment("▼", Style(color=white))

        position_ratio = position / (virtual_size - window_size)
        position = int(size * position_ratio)

        # Put a block at the current position, keeping our up down indicators
        if position == 0:
            segments[0] = Segment("▲", Style(color=white, reverse=True))
        elif position >= size:
            segments[-1] = Segment("▼", Style(color=white, reverse=True))
        else:
            segments[position] = Segment(" ", Style(color=white, reverse=True))

        return Segments(segments, new_lines=True)

        # GNDN
        if window_size and size and virtual_size and size != virtual_size:
            bar_ratio = virtual_size / size
            thumb_size = max(1, window_size / bar_ratio)

            position_ratio = position / (virtual_size - window_size)
            position = (size - thumb_size) * position_ratio
            print("pr", position_ratio, "pos", position)

            start = int(position * len_bars)
            end = start + ceil(thumb_size * len_bars)

            start_index, start_bar = divmod(max(0, start), len_bars)
            end_index, end_bar = divmod(max(0, end), len_bars)

            upper_back_segment = Segment(blank, Style(bgcolor=back))
            lower_back_segment = Segment(blank, Style(bgcolor=back))

            segments = [upper_back_segment] * int(size)
            segments[end_index:] = [lower_back_segment] * (size - end_index)

            segments[start_index:end_index] = [
                Segment(blank, Style(color=bar, reverse=True))
            ] * (end_index - start_index)
        else:
            style = Style(bgcolor=back)
            segments = [Segment(blank, style=style)] * int(size)

        return Segments(segments, new_lines=True)

#    def __rich_console__(
#        self, console: Console, options: ConsoleOptions
#    ) -> RenderResult:
#        size = (
#            (options.height or console.height)
#            if self.vertical
#            else (options.max_width or console.width)
#        )
#        thickness = (
#            (options.max_width or console.width)
#            if self.vertical
#            else (options.height or console.height)
#        )
#
#        _style = console.get_style(self.style)
#
#        bar = self.render_bar(
#            size=size,
#            window_size=self.window_size,
#            virtual_size=self.virtual_size,
#            position=self.position,
#            vertical=self.vertical,
#            thickness=thickness,
#            back_color=_style.bgcolor or Color.parse("#555555"),
#            bar_color=_style.color or Color.parse("bright_magenta"),
#        )
#        yield bar




class MApp(App):
    CSS = """
        Grid {
            grid-size: 2 1;
        }

        .vscroller {
            border: solid red;
        }

        .vscroller:focus {
            border: solid white;
        }
    """

    def compose(self) -> ComposeResult:
        with Grid():
            with VerticalScroll(classes="vscroller") as self.vs1:
                self.vs1.vertical_scrollbar.renderer = SBR
                yield Static(30 * SAMPLE)

            with VerticalScroll(classes="vscroller") as self.vs2:
                self.vs2.vertical_scrollbar.renderer = SBR
                self.vs2.styles.overflow_y = "scroll"
                yield Static("very little text")

    def on_key(self, event):
        key = event.key
        if key == "q":
            exit()


if __name__ == "__main__":
    app = MApp()
    app.run()
