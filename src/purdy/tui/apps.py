# purdy.tui.apps.py
from textual.app import App, ComposeResult

from purdy.tui.animate import AnimationController, cell_list
from purdy.tui.codebox import BoxSpec, RowSpec
from purdy.tui.purdybox import PurdyBox

# =============================================================================

class PurdyApp(App):
    CSS_PATH = "style.tcss"

    def __init__(self, row_specs, max_height=None):
        super().__init__()
        self.row_specs = row_specs

        # Build the PurdyBox containing all the CodeBoxes first so that
        # they can be populated before Textual mounts everything, then yield
        # it in `compose`
        self.control = PurdyBox(self.row_specs, max_height)

    def compose(self) -> ComposeResult:
        yield self.control.container

    async def on_mount(self):
        # Force focus to our first CodeBox, then start animation
        self.set_focus(self.control.rows[0][0].widget.code_display)
        await self.controller.forwards()

    def run(self):
        self.controller = AnimationController(self)
        super().run()

    def _debug_info(self):
        output = ["==== DEBUG INFO ===="]
        from purdy.content import Code

        for row_index, row in enumerate(self.control.rows):
            for box_index, box in enumerate(row):
                output.append(f"\nRow {row_index} Box {box_index}")
                for section in box.doc:
                    if not isinstance(section, Code):
                        output.append(f"   {section.__class__.__name__}")
                        for line in section.lines:
                            output.append((f"      *{repr(line)}*"))
                    else:
                        output.append("   Code")
                        for line in section.lines:
                            output.append("      Line")
                            for part in line.parts:
                                output.append((
                                    f"      {part.token} : {part.text}*"
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
                if "devtools" in self.features:
                    print(self._debug_info())

# =============================================================================
# Factory Methods
# =============================================================================

class AppFactory:
    @classmethod
    def simple(cls, max_height=None, line_number=None, auto_scroll=False,
            title=None):
        """Creates a purdy display with a single code box inside of it.

        :param max_height: limit the height of the content in the terminal,
            defaults to None
        :param line_number: specify a starting line number for the code box,
            defaults to None
        :param auto_scroll: when True, if content is added to the code box it
            scrolls to the bottom. Defaults to False.
        :param title: a title to include at the top of the codebox, defaults
            to None
        """
        row_specs = [
            RowSpec(1, [BoxSpec(1, line_number, auto_scroll, title=title)])
        ]

        app = PurdyApp(row_specs, max_height)
        app.box = app.control.rows[0][0]
        return app

    @classmethod
    def split(cls, max_height=None, line_number_top=None, auto_scroll_top=False,
            relative_height_top=1, line_number_bottom=None,
            auto_scroll_bottom=False, relative_height_bottom=1,
            top_title=None, bottom_title=None):
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
        :param top_title: a title to include over the top codebox, defaults
            to None
        :param bottom_title: a title to include over the bottom codebox,
            defaults to None
        """
        row_specs = [
            RowSpec(relative_height_top, [
                BoxSpec(1, line_number_top, auto_scroll_top, "b",
                    title=top_title)]),
            RowSpec(relative_height_bottom, [
                BoxSpec(1, line_number_bottom, auto_scroll_bottom,
                    title=bottom_title)])
        ]

        app = PurdyApp(row_specs, max_height)
        app.top = app.control.rows[0][0]
        app.bottom = app.control.rows[1][0]
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
        app.rows = app.control.rows
        return app
