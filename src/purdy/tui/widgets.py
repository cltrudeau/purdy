# purdy.tui.widgets.py
import math

from rich.color import Color
from rich.segment import Segment, Segments
from rich.style import Style

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.scrollbar import ScrollBarRender
from textual.widgets import Static

# =============================================================================

class DarkThinBarRender(ScrollBarRender):
    @classmethod
    def render_bar(cls, size, virtual_size, window_size, position,
            thickness, vertical, back_color, bar_color) -> Segments:
        # Hard code the thickness and colour for now
        return super().render_bar(size, virtual_size, window_size,
            position, 1, vertical, back_color, Color.parse("#333333"))


class LightThinBarRender(ScrollBarRender):
    @classmethod
    def render_bar(cls, size, virtual_size, window_size, position,
            thickness, vertical, back_color, bar_color) -> Segments:
        # Hard code the thickness and colour for now
        return super().render_bar(size, virtual_size, window_size,
            position, 1, vertical, back_color, Color.parse("#999999"))


class TriangleScrollRender(ScrollBarRender):
    NO_INDICATOR = "▮"
    UP_INDICATOR = "▲"
    DOWN_INDICATOR = "▼"
    COLOUR = Color.parse("white")
    BLANK = " "
    LINE_INDICATORS = ["⎺", "⎻", "⎼", "⎽"]

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

        if not (window_size and size and virtual_size and size != virtual_size):
            style = Style(bgcolor=back_color)
            segments = [Segment(cls.BLANK, style=style)] * int(size)
            segments[0] = Segment(cls.NO_INDICATOR, Style(color=cls.COLOUR))
            return Segments(segments, new_lines=True)

        bg_segment = Segment(cls.BLANK, Style(bgcolor=back_color))
        segments = [bg_segment] * int(size)
        segments[0] = Segment(cls.UP_INDICATOR, Style(color=cls.COLOUR))
        segments[-1] = Segment(cls.DOWN_INDICATOR, Style(color=cls.COLOUR))

        # Calculate where the position indicator will go, ensuring it is only
        # on the top or bottom when fully scrolled up or down
        position_ratio = position / (virtual_size - window_size)
        index = int(size * position_ratio)
        if position == 0:
            # Full top position
            segments[0] = Segment(cls.UP_INDICATOR,
                Style(color=cls.COLOUR, underline=True))
        elif index == size:
            # Full bottom position (index calc overreaches)
            segments[-1] = Segment(cls.DOWN_INDICATOR,
                Style(color=cls.COLOUR, underline=True))
        else:
            # Somewhere in-between, position the indicator in the 2nd through
            # 2nd-last positions
            scroll_height = size - 2

            # Number of lines each tick on the scroll bar represents
            line_size = (virtual_size - window_size) / scroll_height
            slot = math.ceil(position / line_size)

            # Fractional position within a line, used to map to the
            # LINE_INCREMENTS so that it looks like it is moving even if it is
            # in the same slot
            frac_line_pos = (position % line_size) / line_size
            if frac_line_pos == 0:
                # Perfect division gives 0, but that is the bottom not the top
                frac_line_pos = 1

            # Convert to an index in the inter-line indicators by apply it as
            # a fraction to the number of indicators, answer will be 1-indexed
            # unless frac_line_pos is zero, so compensate
            pos_index = math.ceil(frac_line_pos * len(cls.LINE_INDICATORS))
            if pos_index != 0:
                pos_index -= 1

            # Slot is 1-indexed, but we need to start in the second position
            # anyway
            segments[slot] = Segment(cls.LINE_INDICATORS[pos_index],
                Style(color=cls.COLOUR))

        return Segments(segments, new_lines=True)


class BlurredTriangleScrollRender(TriangleScrollRender):
    NO_INDICATOR = "▯"
    UP_INDICATOR = "△"
    DOWN_INDICATOR = "▽"
    COLOUR = Color.parse("#555555")


class AlwaysVerticalScroll(ScrollableContainer):
    """A container with vertical layout and an always-on scrollbar on the Y
    axis."""

    DEFAULT_CSS = """
    AlwaysVerticalScroll {
        layout: vertical;
        overflow-x: hidden;
        overflow-y: scroll;
    }
    """

    def on_focus(self, event):
        self.vertical_scrollbar.renderer = TriangleScrollRender

    def on_blur(self, event):
        self.vertical_scrollbar.renderer = BlurredTriangleScrollRender


class CodeWidget(Container):
    def __init__(self, border=""):
        super().__init__(classes="code_widget")

        self.border = border.lower()
        self.pad_top = 0
        self.pad_bottom = 0
        self.pad_left = 0
        self.pad_right = 0

        self.code_display = Static("", classes="code_display")

    def compose(self) -> ComposeResult:
        with Container(classes="effect_holder") as self.effect_holder:
            self.overlay = Container(classes="effect_overlay")
            yield self.overlay

            with Container(classes="code_holder") as self.code_holder:
                with AlwaysVerticalScroll(classes="vscroller") as self.vs:
                    self.vs.vertical_scrollbar.renderer = \
                        BlurredTriangleScrollRender

                    yield self.code_display

                    if "t" in self.border:
                        self.vs.styles.border_top = ("solid", "white")
                        self.pad_top = 1
                    if "b" in self.border:
                        self.vs.styles.border_bottom = ("solid", "white")
                        self.pad_bottom = 1
                    if "r" in self.border:
                        self.vs.styles.border_right = ("solid", "white")
                        self.pad_right = 1
                    if "l" in self.border:
                        self.vs.styles.border_left = ("solid", "white")
                        self.pad_left = 1

    async def on_key(self, event):
        key = event.key
        match key:
            case "alt+pagedown":
                # Scroll down half a page
                pos = (self.vs.scroll_y +
                    self.vs.scrollable_content_region.height // 2)
                self.vs.scroll_to(y=pos)

                # Eat event
                event.stop()
            case "alt+pageup":
                # Scroll up half a page
                pos = (self.vs.scroll_y -
                    self.vs.scrollable_content_region.height // 2)
                self.vs.scroll_to(y=pos)

                # Eat event
                event.stop()
