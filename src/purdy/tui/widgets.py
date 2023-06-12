# -*- coding: utf-8 -*-
"""This module implements a text box that displays a
:class:`purdy.content.Listing` object."""
from dataclasses import dataclass
from logging import getLogger

from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.widgets import Frame, Layout, Divider, PopUpDialog
from asciimatics.widgets.widget import Widget

from purdy.content import Listing
from purdy.parser import token_ancestor, HighlightOn, HighlightOff
from purdy.themes.tui import THEMES, ANCESTORS
from purdy.tui.glayout import GappedLayout

# Logging
logger = getLogger(__name__)

# ===========================================================================

HELP_MESSAGE = """\
Purdy

n -- toggle line numbers
q -- quit

Number Commands:
    These commands expect you to press some numbers before activating the command

h -- highlight the given number
"""

# ===========================================================================

NUM_KEYS = [ord('0') + num for num in range(0, 10)]

class PurdyFrame(Frame):
    def __init__(self, rows, actions, screen, max_height):
        self._num_command = []
        self._animating = False

        frame_height = screen.height
        if max_height is not None:
            frame_height = max_height

        divider_height = len(rows) - 1

        # Process the listing boxes sent in the rows container
        data = {}
        requested_height = 0
        num_requesting = 0
        for index, item in enumerate(rows):

            if isinstance(item, tuple):
                data[item[0].name] = item[0].listing
                data[item[1].name] = item[1].listing

                if item[0].height is not None:
                    requested_height += item[0].height
                    num_requesting += 1
            else:
                data[item.name] = item.listing

                if item.height is not None:
                    requested_height += item.height
                    num_requesting += 1

        space = frame_height - divider_height
        if num_requesting > 0:
            default_row_height = (space - requested_height) // num_requesting
        else:
            default_row_height = space // len(rows)

        # Create and layout the frame

        super(PurdyFrame, self).__init__(screen, frame_height, screen.width,
            x=0, y=0, data=data, has_border=False, can_scroll=False)

        self.set_theme('monochrome')

        for index, item in enumerate(rows):
            last_row = index == len(rows) - 1

            # Height was either specified in the RowSpec, calculated above, or
            # if this is the last row use whatever space remains
            box = item
            if isinstance(item, tuple):
                box = item[0]

            if box.height is None and not last_row:
                box_height = default_row_height
            elif last_row:
                box_height = space
            else:
                box_height = box.height

            logger.debug("*** req=%s box_h=%s sp=%s last=%s", requested_height,
                box_height, space, last_row)

            if isinstance(item, tuple):
                # Twin box
                left = int((screen.width - 1) * item[0].width_ratio)
                right = screen.width - left

                twin_layout = GappedLayout([left, 1, right], gaps=[1],
                    fill_frame=last_row)
                self.add_layout(twin_layout)

                box1 = ListingBox(box_height, name=item[0].name)
                twin_layout.add_widget(box1, 0)
                item[0].widget = box1

                box2 = ListingBox(box_height, name=item[1].name)
                twin_layout.add_widget(box2, 2)
                item[1].widget = box2
            else:
                # Single box
                layout = Layout([1,], fill_frame=last_row)
                self.add_layout(layout)

                box = ListingBox(box_height, name=item.name)
                layout.add_widget(box, 0)
                item.widget = box

            if len(rows) > 1 and (index + 1 < len(rows)):
                layout = Layout([1,])
                self.add_layout(layout)
                layout.add_widget(Divider(), 0)

            space -= box_height

        self.fix()
        logger.debug("**** Sizes %s", self._layouts[0]._column_sizes)

    @property
    def frame_update_count(self):
        if not self._animating:
            return super().frame_update_count

        # Do Animation
        widget = self._layouts[0]._columns[0][0]
        limit = widget._render_limit

        total = 0
        for part in widget._value.lines[limit.line].parts:
            total += len(part.text)

        limit.pos += 1
        if limit.pos > total:
            limit.pos = 0
            limit.line += 1

        if limit.line > len(widget._value.lines) - 1:
            self._animating = False
            widget._render_limit = None

        # Still animating, come back in 3 frames
        return 3

    def process_event(self, event):
        event = super().process_event(event)

        if isinstance(event, KeyboardEvent):
            if event.key_code in NUM_KEYS:
                self._num_command.append(chr(event.key_code))
                return None
            elif event.key_code == ord('h'):
                # Highlight the line in the number command
                widget = self.focussed_widget
                if isinstance(widget, ListingBox):
                    if self._num_command:
                        num = int(''.join(self._num_command))
                    else:
                        num = 1

                    widget._value.highlight(num)

                    self._canvas.refresh()
                    self._num_command = []
                return None
            elif event.key_code == ord('H'):
                widget = self.focussed_widget
                if isinstance(widget, ListingBox):
                    widget._value.highlight_off_all()
                    self._canvas.refresh()

                return None
            elif event.key_code == Screen.KEY_ESCAPE:
                self._num_command = []
                return None
            elif event.key_code == ord('?'):
                self._scene.add_effect(
                    PopUpDialog(self._screen, HELP_MESSAGE, ["OK"],
                        has_shadow=True)
                )
                return None

        return event

# ===========================================================================
# Listing Tools

@dataclass
class _RenderLimit:
    line: int
    pos: int


class _ViewPortPart:
    def __init__(self, fg, attr, bg, text):
        self.fg = None
        if fg:
            self.fg = int(fg)

        self.attr = None
        if attr:
            self.attr = int(attr)

        self.bg = None
        if bg:
            self.bg = int(bg)

        self.text = text

    def force_values(self, default_fg, default_attr, default_bg):
        if self.fg is None:
            self.fg = default_fg
        if self.attr is None:
            self.attr = default_attr
        if self.bg is None:
            self.bg = default_bg


class _ViewPortLine:
    def __init__(self, listing_index, wrap_count=None):
        self.parts = []
        self.text_total = 0
        self.wrap_count = wrap_count
        self.listing_index = listing_index
        self.last_in_wrap = True

    def add_part(self, fg, attr, bg, text):
        self.text_total + len(text)
        self.parts.append(_ViewPortPart(fg, attr, bg, text))

# ---------------------------------------------------------------------------

class ListingProxy:
    def __init__(self, widget=None):
        self._widget = widget

    def __getattr__(self, name):
        fn = getattr(self._widget._value, name)
        return fn

# ---------------------------------------------------------------------------

class ListingBox(Widget):
    """
    A ListingBox is a widget for multi-line read-only text viewing.

    It consists of a framed box with option label.
    """

#    __slots__ = ["_label", "_line", "_column", "_start_line", "_start_column",
#        "_required_height", "_as_string", "_on_change",
#        "_reflowed_text_cache", "_parser", "_readonly", "_line_cursor",
#        "_auto_scroll", ]

    def __init__(self, height, label=None, name=None, as_string=False,
            line_wrap=False, parser=None, on_change=None, **kwargs):
        """
        :param height: The required number of input lines for this ListingBox.
        :param label: An optional label for the widget.
        :param name: The name for the ListingBox.
        :param line_wrap: Whether to wrap at the end of the line.
        :param parser: Optional parser to colour text.

        Also see the common keyword arguments in :py:obj:`.Widget`.
        """
        super(ListingBox, self).__init__(name, **kwargs)
        self._label = label

        self._viewport_row = 0

        self._required_height = height
        self._parser = parser
        self._readonly = True
        self._line_cursor = True
        self._cursor_colour = Screen.COLOUR_WHITE
        self._auto_scroll = False

        self._content = []
        self._listing_stamp = -1

        self._render_limit = None
        #self._render_limit = _RenderLimit(1, 108)

    # ----
    # Rendering

    def _get_stop_values(self, x, h):
        if self._render_limit is None:
            return None, None

        return self._render_limit.line, self._render_limit.pos

    def _paint_scroll_indicators(self, focus_only, fg, attr, bg):
        # Paint the scroll indicators
        if focus_only:
            # Only paint a focus indicator
            mark = '▮' if self._has_focus else '▯'

            self._frame.canvas.paint(
                mark,
                self._x + self._offset + self._w - 1,
                self._y,
                fg, attr, bg)
        else:
            # Paint scroll indicators
            if self._viewport_row != 0:
                # Show up marker if we're not at the top
                mark = '▲' if self._has_focus else '△'
                self._frame.canvas.paint(
                    mark,
                    self._x + self._offset + self._w - 1,
                    self._y,
                    fg, attr, bg)

            if self._viewport_row + self._h < len(self._content):
                # Show down marker if we're not at the bottom
                mark = '▼' if self._has_focus else '▽'
                self._frame.canvas.paint(
                    mark,
                    self._x + self._offset + self._w - 1,
                    self._y + self._h - 1,
                    fg, attr, bg)

    def update(self, frame_no):
        if self._listing_stamp < self._value.change_stamp:
            self._generate_content()

        # Clear out the existing box content
        (default_fg, default_attr, default_bg) = self._pick_colours("readonly")
        self._frame.canvas.clear_buffer(default_fg, default_attr, default_bg,
            self._x + self._offset, self._y, self.width, self._h)

        #logger.debug("***** Cleared canvas x=%s y=%s off=%s w=%s h=%s",
        #    self._x, self._y, self._offset, self.width, self._h)

        # Loop through the content in the view port
        x = self._viewport_row
        h = self._viewport_row + self._h
        focus_only = len(self._content) < self._h

        #logger.debug("******* Updating Viewport")
        #for item in self._content[x:h]:
        #    logger.debug("%s", item)

        stop_index, stop_pos = self._get_stop_values(x, h)
        chars_written = 0
        prev_wrapped = False

        for index, line in enumerate(self._content[x:h]):
            pos = 0

            for line_part in line.parts:
                text = line_part.text
                line_part.force_values(default_fg, default_attr, default_bg)

                # If the stop limiter is in effect, stop rendering when you
                # hit the right piece of text, possibly splitting it
                if stop_pos is not None and line.listing_index == stop_index:
                    if chars_written + len(text) > stop_pos:
                        split_point = stop_pos - chars_written + 1
                        text = text[:split_point]

                #logger.debug("**** Painting x=%s y=%s, (%s,%s,%s) *%s*",
                #    self._x + self._offset + pos, self._y + index,
                #    line_part.fg, line_part.attr, line_part.bg, line_part.text)
                #logger.debug("   chars=%s stop_index=%s stop_pos=%s",
                #    chars_written, stop_index, stop_pos)

                # Paint the text to the screen
                self._frame.canvas.paint(
                    text,
                    self._x + self._offset + pos,
                    self._y + index,
                    line_part.fg, line_part.attr, line_part.bg
                )

                pos += len(text)
                chars_written += len(text)

            if line.listing_index == stop_index and line.last_in_wrap:
                # Stop limiter in effect on this line, we're done
                break

            if not prev_wrapped:
                chars_written = 0

            prev_wrapped = line.wrap_count is None

        self._paint_scroll_indicators(focus_only, default_fg, default_attr,
            default_bg)

    # ----
    # Content Generation

    def _generate_content(self):
        # Process the listing, turning it into what it looks like on the
        # screen
        #
        # Line wrapping may cause some lines in the listing to map to multiple
        # lines in the viewport
        #
        # Each content line is one or more tuples containing colour
        # information and text for display on a viewport line
        self._content = []

        # Split point for wrapping text is one less than width to make room
        # for the scroll indicator
        width = self._w - 1

        for index, line in enumerate(self._value):
            theme = THEMES[line.spec.name]
            ancestors = ANCESTORS[line.spec.name]
            bg = theme['Background']

            # Chunk the listing line into pieces width in size
            pieces = line.wrap_at_length(width)
            for count, piece in enumerate(pieces):
                # Each piece gets its own line in the view
                wrap_count = count
                if len(pieces) == 1:
                    wrap_count = None

                viewport_line = _ViewPortLine(index, wrap_count)

                for part in piece:
                    # Check for Highlight tokens
                    if part.token == HighlightOn:
                        bg = theme['Highlight']
                        continue
                    elif part.token == HighlightOff:
                        bg = theme['Background']
                        continue

                    # Not a highlighting token
                    token = token_ancestor(part.token, ancestors)

                    if isinstance(theme[token], tuple):
                        fg = theme[token][0]
                        attr = theme[token][1]
                    else:
                        fg = theme[token]
                        attr = ''

                    viewport_line.add_part(fg, attr, bg, part.text)

                self._content.append(viewport_line)

        if self._auto_scroll and self._content:
            # Scroll to the bottom
            self._change_line( len(self._content) )

        # Track the state marker of the listing so we can detect when it
        # changes
        self._listing_stamp = self._value.change_stamp

        logger.debug("**** Content built %s", len(self._content))
        for line in self._content:
            logger.debug("   %s",
                (f"_ViewPortLine(listing_index={line.listing_index}, "
                f"wrapcount={line.wrap_count},")
            )
            for part in line.parts:
                logger.debug("      => (%4s,%4s,%4s) *%s*", part.fg, part.attr,
                    part.bg, part.text)

            logger.debug(")")

    # ----
    # Event Management

    def _change_vscroll(self, delta):
        """
        Move the scroll port up/down the specified number of lines.

        :param delta: The number of lines to move (-ve is up, +ve is down).
        """
        self._viewport_row += delta

        try:
            line = self._content[self._viewport_row]

            if delta < 1:
                # Moving up; if the line we land on is a wrapped line treat the
                # whole thing like a single block
                if line.wrap_count is not None:
                    count = 0
                    for i in range(self._viewport_row - 1, 0, -1):
                        compare = self._content[i]
                        if compare.listing_index == line.listing_index:
                            count += 1
                        else:
                            break

                    self._viewport_row -= count
            else:
                # Moving down
                bottom_index = self._viewport_row + self._h - 1
                line = self._content[bottom_index]
                if line.wrap_count is not None:
                    # Destination line is wrapped, advance the whole way
                    count = 0
                    for i in range(bottom_index + 1, len(self._content)):
                        compare = self._content[i]
                        if compare.listing_index == line.listing_index:
                            count += 1
                        else:
                            break

                    self._viewport_row += count
        except IndexError as e:
            # Delta moved outside range, will get dealt with below
            pass

        content_length = len(self._content)
        if self._render_limit:
            content_length = self._render_limit.line + 1

        if self._viewport_row + self._h > content_length:
            self._viewport_row = content_length - self._h

        if self._viewport_row < 0:
            self._viewport_row = 0

    def process_event(self, event):
        if not isinstance(event, KeyboardEvent):
            return event

        # Keyboard event
        if event.key_code == Screen.KEY_PAGE_UP:
            self._change_vscroll(-self._h)
            return None
        elif event.key_code == Screen.KEY_PAGE_DOWN:
            self._change_vscroll(self._h)
            return None
        elif event.key_code == Screen.KEY_UP:
            self._change_vscroll(-1)
            return None
        elif event.key_code == Screen.KEY_DOWN:
            self._change_vscroll(1)
            return None
        elif event.key_code == Screen.KEY_HOME:
            # Go to the top of the view port
            self._change_vscroll( -1 * len(self._content) )
            return None
        elif event.key_code == Screen.KEY_END:
            # Go to the bottom of the view port
            self._change_vscroll( len(self._content) )
            return None
        elif event.key_code == ord('n'):
            self._value.toggle_line_numbers()
            self._generate_content()
            return None

        # Event was not handled
        return event

    def required_height(self, offset, width):
        return self._required_height

    # ----
    # Properties

    @property
    def auto_scroll(self):
        """
        When set to True the ListingBox will scroll to the bottom when created
        or next text is added. When set to False, the current scroll position
        will remain even if the contents are changed.

        Defaults to True.
        """
        return self._auto_scroll

    @auto_scroll.setter
    def auto_scroll(self, new_value):
        self._auto_scroll = new_value

    @property
    def value(self):
        """
        The current value for this ListingBox is a
        :class:`purdy.content.Listing` object.
        """
        if self._value is None:
            self._value = Listing()
        return self._value

    @value.setter
    def value(self, new_value):
        self._listing_stamp = -1
        self._value = new_value
        if new_value is None:
            self._value = Listing()
            return

        self._generate_content()
        self.reset()

    # ----
    # Utilities

    def reset(self):
        # Reset to original data and move to end of the text.
        self._viewport_row = 0

        if self._auto_scroll and self._content:
            # Scroll to the bottom
            self._change_line( len(self._content) )
