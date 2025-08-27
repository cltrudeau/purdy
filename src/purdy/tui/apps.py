# purdy.tui.apps.py

import asyncio
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

from purdy.renderers.textual import to_textual
from purdy.tui.widgets import CodeBox

# =============================================================================
# App
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

# -----------------------------------------------------------------------------

class PurdyApp(App):
    CSS_PATH = "purdy_app.tcss"

    def __init__(self, row_specs, max_height=None):
        super().__init__()
        self.max_height = max_height
        self.row_specs = row_specs
        self.rows = []

        # Build the CodeBoxes first so that they can be populated before
        # Textual mounts everything, then yield them in `compose`
        self.grid_width = 0
        self.grid_height = 0

        for row_num, row_spec in enumerate(self.row_specs):
            self.grid_height += row_spec.height

            self.rows.append([])
            for box_num, box_spec in enumerate(row_spec.boxes):
                if row_num == 0:
                    # Use the first row as the blueprint for the width
                    self.grid_width += box_spec.width

                id_string = f"code_box_{row_num}x{box_num}"
                box = CodeBox(id=id_string, border=box_spec.border)
                box.styles.row_span = row_spec.height
                box.styles.column_span = box_spec.width
                self.rows[-1].append(box)

    def compose(self) -> ComposeResult:
        with Grid() as self.grid:
            if self.max_height is not None:
                self.grid.styles.max_height = self.max_height

            for row in self.rows:
                for box in row:
                    yield box

            self.grid.styles.grid_size_rows = self.grid_height
            self.grid.styles.grid_size_columns = self.grid_width

    def on_mount(self):
        self.set_focus(self.query_one("#code_box_0x0"))

    async def on_key(self, event):
        key = event.key
        print("app key", key)
        match key:
            case "q" | "Q":
                exit()
            case "s":
                print("Got s")
#                self.box.vs.scroll_to(y=15)
            case "h":
                print(50*"=")

# =============================================================================
# Factory Methods
# =============================================================================

def simple(max_height=None, line_number=None, auto_scroll=False):
    """Creates a purdy display with a single code box inside of it.

    :param max_height: limit the height of the content in the terminal,
        defaults to None
    :param line_number: specify a starting line number for the code box,
        defaults to None
    :param auto_scroll: when True, if content is added to the code box it
        scrolls to the bottom. Defaults to False.
    """

    row_specs = [
        RowSpec(1, [BoxSpec(1, line_number, auto_scroll)])
    ]

    app = PurdyApp(row_specs, max_height)
    app.box = app.rows[0][0]
    return app


def split(max_height=None, line_number_top=None, auto_scroll_top=False,
        relative_height_top=1, line_number_bottom=None,
        auto_scroll_bottom=False, relative_height_bottom=1):
    """Creates a purdy display with two code boxes one on top of the other.

    :param max_height: limit the height of the content in the terminal,
        defaults to None
    :param line_number_top: specify a starting line number for the top code
        box, defaults to None
    :param auto_scroll_top: when True, if content is added to the top code box
        it scrolls to the bottom. Defaults to False.
    :param relative_height_top: specify the height of the top code box
        against the bottom one. For example top=1, bottom=1 makes them the
        same size, top=3, bottom=1, makes them be 3/4 and 1/4 of the screen
        respectively
    :param line_number_bottom: specify a starting line number for the bottom
        code box, defaults to None
    :param auto_scroll_bottom: when True, if content is added to the bottom
        code box it scrolls to the bottom. Defaults to False.
    :param relative_height_bottom: specify the height of the bottom code box
        against the top one.
    """
    row_specs = [
        RowSpec(relative_height_top, [
            BoxSpec(1, line_number_top, auto_scroll_top)]),
        RowSpec(relative_height_bottom, [
            BoxSpec(1, line_number_bottom, auto_scroll_bottom)])
    ]

    app = PurdyApp(row_specs, max_height)
    app.top = app.rows[0][0]
    app.bottom = app.rows[1][0]
    return app


def app_factory(row_specs, max_height=None):
    """Creates a TUI screen based on a list of rows, where each row is a list
    of :class:`BoxSpec` classes.

    :param row_specs: list of :class:`RowSpec` objects which describe the
        layout information for each row in the resulting display grid. Each
        `RowSpec` contains a list of :class:`BoxSpec` objects, the sum of
        their widths in each row must be equal.

    :param max_height: Max height of the app within your terminal. Defaults to
        None.
    """
    app = PurdyApp(row_specs, max_height)
    return app
