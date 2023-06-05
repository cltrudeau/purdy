import sys
import logging

from asciimatics.widgets import Frame, Layout, Label, Divider, Text, TextBox, \
    CheckBox, RadioButtons, Button, PopUpDialog, TimePicker, DatePicker, DropdownList, PopupMenu
from asciimatics.effects import Background
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication, InvalidFields
from asciimatics.parsers import AsciimaticsParser

from readbox import ReadBox

# Initial data for the form
form_data = {
    'row0': ['${3,1}0${1}',] + list('12345678'),
    'row1': list('987654321'),
}

logging.basicConfig(filename="debug.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

# =============================================================================
# Frame Definition
# =============================================================================

def global_keyhandler(event):
    if isinstance(event, KeyboardEvent):
        if event.key_code == ord('q') or event.key_code == ord('Q'):
            raise StopApplication("User terminated app")


class MaticsFrame(Frame):
    def __init__(self, screen, height):
        super(MaticsFrame, self).__init__(screen, height, screen.width, y=0,
            data=form_data, has_border=False, can_scroll=False)

        self.set_theme('monochrome')

# =============================================================================
# Row Classes
# =============================================================================

class CodeBox:
    def __init__(self, auto_scroll=True, height=None):
        self.auto_scroll = auto_scroll
        self.height = height

    def create_layout(self, frame, name, divider):
        logger.debug("CodeBox.create_layout(%s, %s)", name, divider)
        layout = Layout([1,])
        frame.add_layout(layout)

        box = ReadBox(self.height, name=name, parser=AsciimaticsParser(),
            line_wrap=True)
        box.line_cursor = False
        layout.add_widget(box, 0)

        if divider:
            layout.add_widget(Divider())


class TwinCodeBox:
    def __init__(self, auto_scroll=True, height=None):
        self.auto_scroll = auto_scroll
        self.height = height

    def create_layout(self, frame, name, divider):
        layout = Layout([1, 1])
        frame.add_layout(layout)

        box = ReadBox(self.height, name=f'{name}_left',
            parser=AsciimaticsParser(), line_wrap=True)
        box.line_cursor = False
        layout.add_widget(box, 0)

        box = ReadBox(self.height, name=f'{name}_right',
            parser=AsciimaticsParser(), line_wrap=True)
        box.line_cursor = False
        layout.add_widget(box, 0)

        if divider:
            layout = Layout([1,])
            frame.add_layout(layout)
            layout.add_widget(Divider())

# =============================================================================
# Window Manager
# =============================================================================

class Tui:
    def __init__(self, rows, settings={}, max_height=None):
        self.rows = rows
        self.max_height = max_height

        # Base settings on defaults, change any overrides passed in
        #self.settings = default_settings
        #for key, value in settings.items():
        #    self.settings[key] = value

    def build_scenes(self, screen, scene):
        if self.max_height is None:
            self.max_height = screen.height

        # Loop through rows and figure out which have requested as specific
        # height
        requested_height = 0
        num_requestors = 0
        for row in self.rows:
            if row.height is not None:
                requested_height += row.height
                num_requestors += 1

        if requested_height > self.max_height:
            raise ValueError( (f"Total requested height ({requested_height}) "
                "exceeds max_height ({max_height})") )

        # Determine the height of the auto-height rows
        num_dividers = len(self.rows) - 1
        fill_amount = self.max_height - requested_height - num_dividers
        auto_height = fill_amount // (len(self.rows) - num_requestors)

        # Create the frame and the rows within it
        self.frame = MaticsFrame(screen, self.max_height)

        for num, row in enumerate(self.rows):
            if row.height is None:
                row.height = auto_height

            divider = num < len(self.rows) - 1
            row.create_layout(self.frame, f'row{num}', divider)

        self.frame.fix()

        # -------
        # Hand control over to Asciimatics
        scenes = [
            Scene([Background(screen), self.frame], -1)
        ]

        screen.play(scenes, stop_on_resize=True, start_scene=scene,
            unhandled_input=global_keyhandler, allow_int=True,)

    def run(self, actions):
        self.actions = actions

        last_scene = None
        while True:
            try:
                Screen.wrapper(self.build_scenes, catch_interrupt=False,
                    arguments=[last_scene])
                sys.exit(0)
            except ResizeScreenError as e:
                last_scene = e.scene

# =============================================================================
# Screen Shortcuts
# =============================================================================

class SimpleScreen(Tui):
    def __init__(self, auto_scroll=True, settings={}, max_height=0):
        rows = [
            CodeBox(auto_scroll=auto_scroll),
        ]

        super().__init__(rows, settings, max_height)


class SplitScreen(Tui):
    def __init__(self, top_auto_scroll=True, bottom_auto_scroll=True,
            settings={}, max_height=0, top_height=None, bottom_height=None):
        rows = [
            CodeBox(auto_scroll=top_auto_scroll, height=top_height),
            CodeBox(auto_scroll=bottom_auto_scroll, height=bottom_height),
        ]

        super().__init__(rows, settings, max_height)
