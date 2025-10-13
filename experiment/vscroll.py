from __future__ import annotations

from math import ceil
from typing import ClassVar, Type

import rich.repr
from rich.color import Color
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment, Segments
from rich.style import Style, StyleType

from textual import events
from textual.geometry import Offset
from textual.message import Message
from textual.reactive import Reactive
from textual.renderables.blank import Blank
from textual.widget import Widget

from textual.scrollbar import ScrollBarRender


class VScrollRender(ScrollBarRender):
#    VERTICAL_BARS: ClassVar[list[str]] = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", " "]
#    BLANK_GLYPH: ClassVar[str] = " "

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
        len_bars = len(bars)

        back = back_color
        #bar = bar_color
        bar = Color.parse("yellow")

        width_thickness = 1
        blank = cls.BLANK_GLYPH * width_thickness

        foreground_meta = {"@mouse.down": "grab"}
        if window_size and size and virtual_size and size != virtual_size:
            bar_ratio = virtual_size / size
            thumb_size = max(1, window_size / bar_ratio)

            position_ratio = position / (virtual_size - window_size)
            position = (size - thumb_size) * position_ratio

            start = int(position * len_bars)
            end = start + ceil(thumb_size * len_bars)

            start_index, start_bar = divmod(max(0, start), len_bars)
            end_index, end_bar = divmod(max(0, end), len_bars)

            print(f"##### {bar_ratio=} {thumb_size=} {position_ratio=} {position=} {start=} {end=} {start_index=} {end_index=}")

            upper = {"@mouse.up": "scroll_up"}
            lower = {"@mouse.up": "scroll_down"}

            upper_back_segment = Segment(blank, Style(bgcolor=back, meta=upper))
            lower_back_segment = Segment(blank, Style(bgcolor=back, meta=lower))

            segments = [upper_back_segment] * int(size)
            segments[end_index:] = [lower_back_segment] * (size - end_index)

            segments[start_index:end_index] = [
                Segment(blank, Style(color=bar, reverse=True, meta=foreground_meta))
            ] * (end_index - start_index)

            print("*****", segments)
        else:
            style = Style(bgcolor=back)
            segments = [Segment(blank, style=style)] * int(size)

        return Segments(segments, new_lines=True)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        print("### RC", dir(self))
        yield from super().__rich_console__(console, options)
