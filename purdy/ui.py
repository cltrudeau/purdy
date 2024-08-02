"""
UI (purdy.ui.py)
================

This module is the entry point for the code viewers. It is a lightweight proxy
to implementation of a screen. Screen implementations are found in
:mod:`purdy.iscreen`.  All programs using the purdy library need to create a
:class:`Screen` object or one of its children. The factory in this module
determines which actual implementation is loaded.
"""
import argparse, sys

from purdy.animation.manager import AnimationManager
from purdy.animation.cell import group_steps_into_cells
from purdy.cmd import background_arg, max_height_arg
from purdy.content import Listing
from purdy.settings import settings as default_settings

#import logging
#logging.basicConfig(filename='debug.log', level=logging.DEBUG)
#logger = logging.getLogger()

# =============================================================================

DESCRIPTION = """You can alter the behaviour of any script calling
Screen.run() by passing in command line arguments."""

class Factory:
    name = 'tui'
    iscreen = None

    @classmethod
    def get_iscreen_class(cls):
        if cls.name == 'tui':
            from purdy.iscreen.tui.iscreen import TUIScreen
            return TUIScreen
        elif cls.name == 'virtual':
            from purdy.iscreen.virtual.iscreen import VirtualScreen
            return VirtualScreen
        elif cls.name == 'exercise':
            from purdy.iscreen.exercise.iscreen import ExerciseScreen
            return ExerciseScreen

# =============================================================================
# Screen
# =============================================================================

class VirtualCodeWidget:
    """Render hook implementation used with the :class:`VirtualCodeBox`.
    """
    def __init__(self):
        self.lines = []

    #--- RenderHook methods
    def line_inserted(self, listing, position, line):
        content = listing.render_line(line)
        index = position - 1
        self.lines.insert(index, content)

    def line_removed(self, listing, position):
        del self.lines[position - 1]

    def line_changed(self, listing, position, line):
        content = listing.render_line(line)
        index = position - 1
        self.lines[index] = content

    def clear(self):
        self.lines = []


class VirtualCodeBox:
    """Specifies a box to contain code. This implementation is not meant to be
    associated with a :class:`Screen`. Used for "rendering" off screen,
    manipulating code either for export or copying to a concrete code box
    later

    :param starting_line_number: -1 means no line numbers, anything larger will 
                                 be the first line number displayed.  Defaults 
                                 to -1
    """
    def __init__(self, starting_line_number=-1, display_mode='plain'):
        self.starting_line_number = starting_line_number
        self.listing = Listing(starting_line_number=starting_line_number)
        self.widget = VirtualCodeWidget()

        self.listing.set_display(display_mode, self.widget)

    def perform_actions(self, actions):
        """Performs the list of actions on the code in the box. Done separtely
        from the main event loop so it has no interactions like Wait,
        typewriters, etc. Everything is done in fast-forward mode.

        :param actions: list of actions to perfrom on the code in this box
        """
        for action in actions:
            for step in action.steps():
                step.render_step()

# -----------------------------------------------------------------------------

class CodeBox:
    """Specifies a box to contain code. :class:`Screen` uses these to
    determine widget layout, subsequent actions are done within the context of 
    this box. When :func:`CodeBox.build` is called by a :class:`Screen` class
    a widget is built and this box is added to the screen.

    :param starting_line_number: -1 means no line numbers, anything larger will 
                                 be the first line number displayed.  Defaults 
                                 to -1

    :param auto_scroll: When True, :class:`purdy.widgets.CodeBox` created by 
                        this specification automatically scrolls to newly added 
                        content.  Defaults to True.

    :param height: Number of lines the row containing this box should be.  A 
                   value of 0 indicates automatic spacing.  Defaults to 0.

    :param compact: if False, the dividing line between this box and the next 
                    has a 1-line empty boundary. Parameter is ignored if there 
                    is no item after this one in the rows=[] listing. Defaults 
                    to False
    """
    def __init__(self, starting_line_number=-1, auto_scroll=True, height=0, 
            compact=False):
        self.starting_line_number = starting_line_number
        self.auto_scroll = auto_scroll
        self.height = height
        self.compact = compact
        self.listing = Listing(starting_line_number=starting_line_number)

    def setup(self, screen):
        self.screen = screen
        self.screen.code_boxes.append(self)

    def build(self, screen):
        self.screen.iscreen.add_code_box(self)


class TwinCodeBox:
    """Specifies two side-by-side CodeBoxes. The contained CodeBoxes can be
    either accessed as twin.left and twin.right, or twin[0] and twin[1]. When
    :func:`TwinCodeBox.build` is called, the widgets are created and added to 
    the :attr:`Screen.code_boxes` list sequentially, i.e. a single
    TwinCodeBox results in two CodeBox items in Screen's list.

    :param left_starting_line_number:
    :param right_starting_line_number: -1 to turn line numbers off, any higher 
                                       value is the first number to display. 
                                       Defaults to -1

    :param left_auto_scroll:
    :param right_auto_scroll: True to specify that scrolling happens
                              automatically for the left and right boxes
                              created by this spec. Defaults to True.

    :param left_weight:
    :param right_weight: relative weights for the widths of the columns, if the 
                          values are the same then the columns are the same
                          width, otherwise the widths are formed based on the
                          ratio of left:right. Example: left_weight=2,
                          right_weight=1 means the left side will be twice the
                          width of the right side. Both values default to 1.

    :param height: number of lines for the row this set of boxes is in.  The 
                   default of 0 specifies automatic height

    :param compact: if False, the dividing line between this box and the next 
                    has a 1-line empty boundary. Parameter is ignored if there
                    is no item after this one in the rows=[] listing. Defaults
                    to False
    """
    def __init__(self, left_starting_line_number=-1, left_auto_scroll=True, 
            left_weight=1, right_starting_line_number=-1, 
            right_auto_scroll=True, right_weight=1, height=0, compact=False):

        self.left_starting_line_number = left_starting_line_number
        self.left_auto_scroll = left_auto_scroll
        self.left_weight = left_weight
        self.right_starting_line_number = right_starting_line_number
        self.right_auto_scroll = right_auto_scroll
        self.right_weight = right_weight
        self.height = height
        self.compact = compact

    def setup(self, screen):
        class Side:
            pass

        self.screen = screen
        self.left = Side()
        self.left.code_box = CodeBox(self.left_starting_line_number,
            self.left_auto_scroll)
        self.left.code_box.setup(screen)

        self.right = Side()
        self.right.code_box = CodeBox(self.right_starting_line_number,
            self.right_auto_scroll)
        self.right.code_box.setup(screen)

    def build(self, screen):
        self.screen.iscreen.add_twin_code_box(self)


class Screen:
    """Represents the main UI window for the TUI application. The layout is
    specified by passing in one or more :class:`CodeBox` or
    :class:`TwinCodeBox` objects to the constructor. Each box will have a
    corresponding :class:`purdy.widgets.CodeWidget` inside of the UI for
    displaying code.

    :param settings: a settings dictionary object. Defaults to `None` which 
                     uses the default settings dictionary: 
                     :attr:`settings.settings`

    :param rows: a list containing one or more :class:`CodeBox` or 
                 :class:`TwinCodeBox` definitions, to specify the layout of 
                 the screen

    :param max_height: maximum display height in TUI mode, defaults to 0,
                       meaning no max

    Example:

    .. code-block:: python

        from purdy.actions import AppendAll
        from purdy.content import Code
        from purdy.ui import Screen, CodeBox, TwinCodeBox

        screen = Screen(rows=[TwinCodeBox(height=8),
                CodeBox(auto_scroll=False)])

        c1 = Code(contents_filename='c1.py', starting_line_number=1)
        c2 = Code(contents_filename='c2.py')
        c3 = Code(contents_filename='c3.py')

        actions = [
            AppendAll(screen.code_boxes[0], c1),
            AppendAll(screen.code_boxes[1], c2),
            AppendAll(screen.code_boxes[2], c3),
        ]

        screen.run(actions)

    The above would produce a screen with two rows, the first row having two 
    :class:`purdy.widgets.CodeWidget` objects side by side, the second having a
    single one. The top left box would have line numbers turned on, both top
    boxes are 8 lines tall, and the bottom box has auto scrolling turned off.

    The screen would be divided like this:

    +-----------+-----------+
    |           |           |
    |           |           |
    +-----------+-----------+
    |                       |
    |                       |
    |                       |
    |                       |
    +-----------------------+

    **Command Line Parameters**

    Unless "deactivate_args" is set to True in :mod:`purdy.settings` (False by
    default), Screen will also parse command line arguments. This allows
    scripts calling the library to change their behaviour with switches. 

    Supported switches are:

    * **--debugsteps** Print out the animation steps, grouped by Cell and exit
    * **--export** Print out the results of the actions
    * **--exportrtf** Print out the results of the actions in RTF format

    """
    def __init__(self, settings=None, rows=[], max_height=0):
        self.rows = rows
        self.max_height = max_height
        self.code_boxes = []
        self.concrete_boxes = []

        self.settings = settings
        if settings is None:
            self.settings = default_settings

        self.movie_mode = self.settings['movie_mode']
        if self.movie_mode != -1:
            self.movie_mode = float(self.movie_mode) / 1000.0

        self.animation_manager = AnimationManager(self)

        for row in self.rows:
            row.setup(self)

    def _get_args(self):
        class Dummy:
            pass

        # Screen can be influenced by command line arguments
        parser = argparse.ArgumentParser(description=DESCRIPTION)
        parser.add_argument('--debugsteps', '--ds', action='store_true', 
            help='Print out the animation steps, grouped by Cell and exit')

        parser.add_argument('--export', action='store_true', 
            help='Print out the results of the actions')

        parser.add_argument('--exportrtf', action='store_true', 
            help='Print out the results of the actions in RTF format')

        background_arg(parser)
        max_height_arg(parser)

        if self.settings['deactivate_args']:
            # Ignore whatever was passed in on command line because of the
            # settings
            self.args = parser.parse_args([])
        else:
            self.args = parser.parse_args()
            if self.args.maxheight:
                self.max_height = self.args.maxheight

    def load_actions(self, actions):
        steps = []
        for (index, action) in enumerate(actions):
            try:
                steps.extend( action.steps() )
            except:
                tb = sys.exc_info()[2]
                raise RuntimeError( ('An exception occurred while loading '
                    f'action #{index+1}: {action.__class__.__name__}'
                    )).with_traceback(tb)

        cells = group_steps_into_cells(steps)
        self.animation_manager.register(cells)

    def set_alarm(self, handler, when):
        return self.iscreen.set_alarm(handler, when)

    def remove_alarm(self, alarm_handle):
        self.iscreen.remove_alarm(alarm_handle)

    def run(self, actions):
        """Calls the main display event loop. Does not return until the UI
        exits."""
        #logger.debug(55*'=')
        self._get_args()
        self.actions = actions

        if self.args.export or self.args.exportrtf:
            Factory.name = 'virtual'

        # Create concrete instances of iscreen an boxes
        klass = Factory.get_iscreen_class()
        self.iscreen = klass(self)
        for row in self.rows:
            row.build(self)

        # Process the actions
        self.load_actions(actions)

        if self.args.debugsteps:
            for cell in self.animation_manager.cells:
                print(f'{cell.__class__.__name__}')
                for step in cell.steps:
                    print('   step', step)
            exit()

        self.iscreen.run()

# =============================================================================
# Other Screens
# =============================================================================

class SplitScreen(Screen):
    """Convenience implementation of :class:`Screen` that supports two 
    :class:`CodeBox` instances, stacked vertically and separated by a dividing
    line. The code boxes are :attr:`SplitScreen.top` and
    :attr:`SplitScreen.bottom`. 

    :param settings: a settings dictionary object. Defaults to `None` which 
                     uses the default settings dictionary: 
                     :attr:`settings.settings`

    :param top_starting_line_number: starting line number for the top 
                                     code box

    :param top_auto_scroll: When True, the top :class:`ui.CodeBox` 
                            automatically scrolls to newly added content.
                            Defaults to True.

    :param bottom_starting_line_number: starting line number for the 
                                        bottom code box

    :param bottom_auto_scroll: When True, the bottom :class:`ui.CodeBox` 
                            automatically scrolls to newly added content.
                            Defaults to True.

    :param top_height: Number of lines the top box should be. A value of 0
                       indicates top and bottom should be the same size.
                       Defaults to 0.

    :param compact: True if for the dividing line between the top and bottom 
                    screens is to have no margin. Defaults to False

    :param max_height: maximum display height in TUI mode, defaults to 0,
                       meaning no max
    """
    def __init__(self, settings=None, top_starting_line_number=-1, 
            top_auto_scroll=True, bottom_starting_line_number=-1,
            bottom_auto_scroll=True, top_height=0, compact=False, 
            max_height=0):
        self.top = CodeBox(top_starting_line_number, top_auto_scroll, 
            top_height, compact=compact)
        self.bottom = CodeBox(bottom_starting_line_number, bottom_auto_scroll)
        super().__init__(settings, rows=[self.top, self.bottom], 
            max_height=max_height)


class SimpleScreen(Screen):
    """Convenience implementation of :class:`Screen` that supports a single
    :class:`CodeBox`.  The code box is available as 
    :attr:`SimpleScreen.code_box`.

    :param settings: a settings dictionary object. Defaults to `None` which 
                     uses the default settings dictionary: 
                     :attr:`settings.settings`
    
    :param starting_line_number: starting line number for the created code
                                 box
    :param auto_scroll: When True, the class:`ui.CodeBox` automatically 
                        scrolls to newly added content.  Defaults to True.

    :param max_height: maximum display height in TUI mode, defaults to 0,
                       meaning no max
    """
    def __init__(self, settings=None, starting_line_number=-1, 
            auto_scroll=True, max_height=0):
        """Foo man chooo"""
        self.code_box = CodeBox(starting_line_number, auto_scroll)
        super().__init__(settings, [self.code_box], max_height=max_height)

    def thing(self):
        pass
