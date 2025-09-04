# purdy.tui.codebox.py
import asyncio
import random

from dataclasses import dataclass

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

from purdy.content import Code
from purdy.renderers.textual import to_textual
from purdy.tui import animate
from purdy.tui.widgets import CodeWidget

# =============================================================================
# Specs Used to Define The Layout
# =============================================================================

@dataclass
class BoxSpec:
    """Used to describe each text area in the app that will be showing
    code.

    :param width: relative width based on other boxes in the row. For example,
        row_specs=[Box_Spec(2), BoxSpec(1)] results in a single row where the
        first box takes up 2/3rds of the space.

    :param line_number: Starting line number for code displayed in the box.
        Defaults to None

    :param auto_scroll: True to scroll down when content gets added

    :param border: A string specifying which borders are on for this box.
        Expects the letters "t", "b", "l", "r" in any order for turning on the
        top, bottom, left, and right borders respectively. Defaults to no
        borders.
    """

    width: int
    line_number: int = None
    auto_scroll: bool = False
    border: str = ""


@dataclass
class RowSpec:
    """Container for a row of :class:`BoxSpec` objects to describe a row in
    the display grid.

    :param height: relative height of this row in comparison to others in the
        grid. For example [RowSpec(2, ...), RowSpec(1,...)] produces two rows
        with the first taking up 2/3rds of the height of the screen.

    :param boxes: a list of :class:`BoxSpec` objects in this row
    """
    height: int
    boxes: list

# =============================================================================
# Code Abstraction
# =============================================================================

class CodeBox:
    def __init__(self, row_spec, box_spec):
        self.box_spec = box_spec
        self.last_after = None

        self.holder = CodeWidget(border=box_spec.border)
        self.holder.styles.row_span = row_spec.height
        self.holder.styles.column_span = box_spec.width

    def __repr__(self):
        return "CodeBox()"

    def update(self, content):
        self.holder.code_display.update(content)

        if self.box_spec.auto_scroll:
            self.holder.vs.scroll_end()

    def _process_content(self, content):
        if isinstance(content, Code):
            self.last_parser = content.parser

    # --- Animation Actions
    def append(self, content):
        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        after = before + content
        animate.cell_list.append(animate.Cell(self, before, after))
        self.last_after = after
        return self

    def replace(self, content):
        if self.last_after is not None:
            before = self.last_after
        else:
            before = ""

        after = content
        animate.cell_list.append(animate.Cell(self, before, after))
        self.last_after = after
        return self

    def pause(self, pause, pause_variance=None):
        if pause_variance is not None:
            pause = random.uniform(pause, pause + pause_variance)

        animate.cell_list.append(animate.PauseCell(pause))
        return self

    def wait(self):
        animate.cell_list.append(animate.WaitCell())
        return self
