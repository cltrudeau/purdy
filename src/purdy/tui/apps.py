# purdy.tui.apps.py
from textual import on
from textual.app import App, ComposeResult
from textual.containers import (Center, Container, Horizontal, Vertical,
VerticalScroll)
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from purdy.tui.animate import AnimationController, cell_list
from purdy.tui.codebox import BoxSpec, RowSpec
from purdy.tui.purdybox import PurdyBox

# =============================================================================

HELP_TEXT_TITLE = "[white bold]Purdy Help[/]"

HELP_TEXT = [
    ("[white bold]right arrow[/] - ", "Advanced to next animation", False),
    ("[white bold]left arrow[/] - ", "Go back an animation", False),
    ("[white bold]s[/] - ",
        "Skip the current animation, or past the next one", True),
    ("[white bold]0-9[/] - ", "One or more numbers can be combined before pressing skip or backwards to perform multiple operations", True),
    ("[white bold]alt+page down[/] - ",
        "Half page down on a scrollable text window", False),
    ("[white bold]alt+page up[/] - ",
        "Half page up on a scrollable text window", True),
    ("[white bold]ESC[/] - ", "Clear the number count", False),
    ("[white bold]h[/] - ", "This help message, but you knew that", False),
    ("[white bold]q[/] - ", "Quit", False),
]

class HelpDialogScreen(ModalScreen):
    def compose(self):
        with Vertical(id="help_dialog_box"):
            yield Static(HELP_TEXT_TITLE, id="help_dialog_title")
            with VerticalScroll():
                for key, desc, space in HELP_TEXT:
                    classes = "help_dialog_item_container"
                    if space:
                        classes += " help_dialog_extra_pad"

                    with Horizontal(classes=classes):
                        yield Static(key, classes="help_dialog_key_col")
                        with Container(classes="help_dialog_desc_holder"):
                            yield Static(desc, classes="help_dialog_desc_col")

            with Center(id="help_dialog_button_holder"):
                button = Button("Ok", id="help_dialog_ok")
                yield button
                button.focus()

    @on(Button.Pressed, "#help_dialog_ok")
    def on_button_pressed(self):
        self.app.pop_screen()

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

        self.repeat_count = ""

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
            case "ESC":
                self.repeat_count += ""
            case "right":
                await self.controller.forwards()
            case "left":
                count = 1
                if self.repeat_count:
                    count = int(self.repeat_count)

                for _ in range(0, count):
                    await self.controller.backwards()

                self.repeat_count = ""
            case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
                self.repeat_count += key
            case "d":
                if "devtools" in self.features:
                    print(self._debug_info())
            case "h":
                self.push_screen(HelpDialogScreen())
            case "q" | "Q":
                exit()
            case "s":
                count = 1
                if self.repeat_count:
                    count = int(self.repeat_count)

                for _ in range(0, count):
                    await self.controller.skip()

                self.repeat_count = ""

# =============================================================================
# Factory Methods
# =============================================================================

class AppFactory:
    """Factory methods for creating a purdy app."""

    @classmethod
    def simple(cls, max_height=None, line_number=None, auto_scroll=False,
            title=None):
        """Creates a purdy display with a single
        :class:`~purdy.tui.codebox.CodeBox` inside of it.

        :param max_height: limit the height of the content in the terminal,
            defaults to None
        :param line_number: specify a starting line number for the code box,
            defaults to None
        :param auto_scroll: when True, if content is added to the code box it
            scrolls to the bottom. Defaults to False.
        :param title: a title to include at the top of the
            :class:`purdy.tui.codebox.CodeBox`, defaults to None
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
        """Creates a purdy display with two :class:`~purdy.tui.codebox.CodeBox`
        objects one on top of the other.

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
        :param top_title: a title to include over the top
            :class:`~purdy.tui.codebox.CodeBox`, defaults to None
        :param bottom_title: a title to include over the bottom
            :class:`~purdy.tui.codebox.CodeBox`, defaults to None
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
        list of :class:`~purdy.tui.codebox.BoxSpec` classes.

        :param row_specs: list of :class:`~purdy.tui.codebox.RowSpec` objects
            which describe the layout information for each row in the
            resulting display grid. Each `RowSpec` contains a list of
            :class:`~.purdy.tui.codebox.BoxSpec` objects, the sum of their
            widths in each row must be equal.

        :param max_height: Max height of the app within your terminal.
            Defaults to None.
        """
        app = PurdyApp(row_specs, max_height)
        app.rows = app.control.rows
        return app
