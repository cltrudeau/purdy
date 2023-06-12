# -*- coding: utf-8 -*-
"""This module implements the displaying of widgets appropriately"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from builtins import range
from builtins import object
from logging import getLogger
from wcwidth import wcswidth
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.exceptions import Highlander, InvalidFields
from asciimatics.screen import Screen
from asciimatics.utilities import _DotDict
from asciimatics.widgets.utilities import _euclidian_distance
from asciimatics.widgets.widget import Widget

from asciimatics.widgets.layout import Layout

# Logging
logger = getLogger(__name__)


class GappedLayout(Layout):
    """
    Widget layout handler with optional gaps between columns.

    """

    __slots__ = ["_column_sizes", "_columns", "_frame", "_has_focus", "_live_col", "_live_widget",
                 "_fill_frame", "_gaps"]

    def __init__(self, columns, fill_frame=False, gaps=[]):
        """
        :param columns: A list of numbers specifying the width of each column in this layout.
        :param fill_frame: Whether this Layout should attempt to fill the rest of the Frame.
            Defaults to False.
        :param gaps: a list of gaps between each column in character widths,
            can be partially filled, example gaps=[1] for a 3-column layout
            produces a gap of 1 between the first two columns an no gap
            between columns 2  & 3.

        """
        total_size = sum(columns)
        self._column_sizes = [x / total_size for x in columns]
        self._columns = [[] for _ in columns]
        self._frame = None
        self._has_focus = False
        self._live_col = 0
        self._live_widget = -1
        self._fill_frame = fill_frame
        self._gaps = gaps

    def fix(self, start_x, start_y, max_width, max_height):
        """
        Fix the location and size of all the Widgets in this Layout.

        :param start_x: The start column for the Layout.
        :param start_y: The start line for the Layout.
        :param max_width: Max width to allow this layout.
        :param max_height: Max height to allow this layout.
        :returns: The next line to be used for any further Layouts.
        """
        total_gap = sum(self._gaps)
        x = start_x
        width = max_width - total_gap
        y = w = 0
        max_y = start_y
        string_len = wcswidth if self._frame.canvas.unicode_aware else len
        dimensions = []
        for i, column in enumerate(self._columns):
            # For each column determine if we need a tab offset for labels.
            # Only allow labels to take up 1/3 of the column.
            if len(column) > 0:
                offset = max([0 if c.label is None else string_len(c.label) + 1 for c in column])
            else:
                offset = 0
            offset = int(min(offset,
                         width * self._column_sizes[i] // 3))

            # Start tracking new column
            dimensions.append(_DotDict())
            dimensions[i].parameters = []
            dimensions[i].offset = offset

            # Do first pass to figure out the gaps for widgets that want to fill remaining space.
            fill_layout = None
            fill_column = None
            y = start_y
            w = int(width * self._column_sizes[i])
            for widget in column:
                h = widget.required_height(offset, w)
                if h == Widget.FILL_FRAME:
                    if fill_layout is None and fill_column is None:
                        dimensions[i].parameters.append([widget, x, w, h])
                        fill_layout = widget
                    else:
                        # Two filling widgets in one column - this is a bug.
                        raise Highlander("Too many Widgets filling Layout")
                elif h == Widget.FILL_COLUMN:
                    if fill_layout is None and fill_column is None:
                        dimensions[i].parameters.append([widget, x, w, h])
                        fill_column = widget
                    else:
                        # Two filling widgets in one column - this is a bug.
                        raise Highlander("Too many Widgets filling Layout")
                else:
                    dimensions[i].parameters.append([widget, x, w, h])
                    y += h

            # Note space used by this column.
            dimensions[i].height = y

            # Update tracking variables fpr the next column.
            max_y = max(max_y, y)
            x += w
            try:
                # Shift the x by any gap
                x += self._gaps[i]
            except IndexError:
                pass

        # Finally check whether the Layout is allowed to expand.
        if self.fill_frame:
            max_y = max(max_y, start_y + max_height)

        # Now apply calculated sizes, updating any widgets that need to fill space.
        for column in dimensions:
            y = start_y
            for widget, x, w, h in column.parameters:
                if h == Widget.FILL_FRAME:
                    h = max(1, start_y + max_height - column.height)
                elif h == Widget.FILL_COLUMN:
                    h = max_y - column.height
                widget.set_layout(x, y, column.offset, w, h)
                y += h

        return max_y
