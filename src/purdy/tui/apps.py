# purdy.tui.apps.py
from textual.app import App, ComposeResult
from textual.containers import Grid

from purdy.tui.animate import AnimationController, cell_list
from purdy.tui.codebox import BoxSpec, CodeBox, RowSpec, TText

# =============================================================================

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

                box = CodeBox(row_spec, box_spec)
                self.rows[-1].append(box)

    def compose(self) -> ComposeResult:
        with Grid() as self.grid:
            if self.max_height is not None:
                self.grid.styles.max_height = self.max_height

            # Loop through the CodeBoxes and compose their widgets
            for row in self.rows:
                for box in row:
                    yield box.holder

            self.grid.styles.grid_size_rows = self.grid_height
            self.grid.styles.grid_size_columns = self.grid_width

    async def on_mount(self):
        # Force focus to our first CodeBox, then start animation
        self.set_focus(self.rows[0][0].holder.code_display)
        await self.controller.forwards()

    def run(self):
        self.controller = AnimationController(self)
        super().run()

    def _debug_info(self):
        output = ["==== DEBUG INFO ===="]

        for row_index, row in enumerate(self.rows):
            for box_index, box in enumerate(row):
                output.append(f"\nRow {row_index} Box {box_index}")
                for item in box.doc.items:
                    if isinstance(item, TText):
                        output.append(f"   TText: *{repr(item)}*")
                    elif isinstance(item, str):
                        output.append(f"   String: *{repr(item)}*")
                    else:
                        output.append("    MultiCode")
                        for code in item:
                            output.append("       Code")
                            for line in code.lines:
                                output.append("          Line")
                                for part in line.parts:
                                    output.append((
                                        "             "
                                        f"{part.token} : {part.text}*"
                                    ))

        output.append("\nCell list:")
        for count, cell in enumerate(cell_list):
            output.append(f"   {count} {cell}")

        return "\n".join(output)

    async def on_key(self, event):
        key = event.key
        match key:
            case "q" | "Q":
                exit()
            case "right":
                await self.controller.forwards()
            case "left":
                await self.controller.backwards()
            case "s":
                await self.controller.skip()
            case "d":
                print(self._debug_info())

# =============================================================================
# Factory Methods
# =============================================================================

class AppFactory:
    @classmethod
    def simple(cls, max_height=None, line_number=None, auto_scroll=False):
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

    @classmethod
    def split(cls, max_height=None, line_number_top=None, auto_scroll_top=False,
            relative_height_top=1, line_number_bottom=None,
            auto_scroll_bottom=False, relative_height_bottom=1):
        """Creates a purdy display with two code boxes one on top of the other.

        :param max_height: limit the height of the content in the terminal,
            defaults to None
        :param line_number_top: specify a starting line number for the top code
            box, defaults to None
        :param auto_scroll_top: when True, if content is added to the top code
            box it scrolls to the bottom. Defaults to False.
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
                BoxSpec(1, line_number_top, auto_scroll_top, "b")]),
            RowSpec(relative_height_bottom, [
                BoxSpec(1, line_number_bottom, auto_scroll_bottom)])
        ]

        app = PurdyApp(row_specs, max_height)
        app.top = app.rows[0][0]
        app.bottom = app.rows[1][0]
        return app

    @classmethod
    def full(cls, row_specs, max_height=None):
        """Creates a TUI screen based on a list of rows, where each row is a
        list of :class:`BoxSpec` classes.

        :param row_specs: list of :class:`RowSpec` objects which describe the
            layout information for each row in the resulting display grid. Each
            `RowSpec` contains a list of :class:`BoxSpec` objects, the sum of
            their widths in each row must be equal.

        :param max_height: Max height of the app within your terminal.
            Defaults to None.
        """
        app = PurdyApp(row_specs, max_height)
        return app
