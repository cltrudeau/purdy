"""
UI (purdy.ui.py)
================

This module is the entry point for the Urwid based code viewer included in
purdy. All programs using the purdy library need to create a :class:`Screen`
object or one of its children.
"""
import argparse

import urwid

from purdy.animation.manager import AnimationManager
from purdy.animation.cell import group_steps_into_cells
from purdy.colour import UrwidColourizer
from purdy.content import Listing
from purdy.settings import settings as default_settings
from purdy.widgets import CodeWidget, DividingLine, TwinContainer

#import logging
#logging.basicConfig(filename='debug.log', level=logging.DEBUG)
#logger = logging.getLogger()

# =============================================================================

DESCRIPTION = """You can alter the behaviour of any script calling
Screen.run() by passing in command line arguments."""

# =============================================================================
# Main Screen
# =============================================================================

class FocusWalker:
    ### Urwid has no call for focusing on a widget, you have to use an index
    # into its parent's container. The FocusWalker finds all of the CodeWidget
    # objects, figures out which one is currently focused and allows for the
    # previous and next item to be focused
    class Node:
        def __init__(self, position, parent=None, parent_position=0):
            self.position = position
            self.parent = parent
            self.parent_position = parent_position

    def __init__(self, root):
        ### Figures out the order things should be focused in. 
        #
        # :param root: root container to look for CodeWidgets within
        #
        self.root = root
        self.focused_index = 0
        self.nodes = []

        current_focus, _ = root.contents[root.focus_position]

        # root is a Pile with either CodeWidgets or Columns in it, where
        # the columns contain CodeWidgets
        for position, content in enumerate(root.contents):
            widget = content[0]
            if isinstance(widget, CodeWidget):
                if widget == current_focus:
                    self.focused_index = len(self.nodes)

                self.nodes.append( self.Node(position) )
            elif isinstance(widget, urwid.Columns):
                index = len(self.nodes)

                self.nodes.append( self.Node(position, widget, 0) )
                self.nodes.append( self.Node(position, widget, 1) )

                if widget == current_focus:
                    if widget.focus_position == 0:
                        self.focused_index = index
                    elif widget.focus_position == 1:
                        self.focused_index = index + 1
                    # else: shouldn't happen

            # else: shouldn't happen

    def focus_next(self):
        # if we're the last item, loop to the next
        position = self.focused_index + 1
        if position >= len(self.nodes):
            position = 0

        self.set_focus(position)

    def focus_prev(self):
        # if we're the first item, loop to the next
        position = self.focused_index - 1
        if position < 0:
            position = len(self.nodes) - 1

        self.set_focus(position)

    def set_focus(self, position):
        # set the focus
        node = self.nodes[position]
        self.root.focus_position = node.position

        if node.parent:
            node.parent.focus_position = node.parent_position


class BaseWindow(urwid.Pile):
    def __init__(self, screen, *args, **kwargs):
        self.screen = screen
        self.animation_manager = AnimationManager(screen)
        super(BaseWindow, self).__init__(*args, **kwargs)

    def _next_focus(self):
        walker = FocusWalker(self)
        walker.focus_next()

    def _prev_focus(self):
        walker = FocusWalker(self)
        walker.focus_prev()

    def keypress(self, size, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        if key in ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10'):
            # let parent handle function keys
            return super(BaseWindow, self).keypress(size, key)

        if key not in self.animation_manager.handled_keys: 
            # handle keys not handled by the animation manager 
            result = super(BaseWindow, self).keypress(size, key)
            if result is None:
                # keypress was handled by child, we're done
                return None
            # else: fall through if super().keypress() didn't deal with it

        if self.screen.movie_mode > -1:
            # Ignore other keypresses in movie mode
            return None

        # --- at this point the keypress was not handled by the children, see
        # if we want to do anything with it
        if key == 'tab':
            self._next_focus()
            return None

        if key == 'shift tab':
            self._prev_focus()

        return self.animation_manager.perform(key)

    def animation_alarm(self, loop, data):
        self.animation_manager.animation_alarm()

    def movie_alarm(self, loop, data):
        self.animation_manager.movie_alarm()

    def first_alarm(self, loop, data):
        self.animation_manager.first_alarm()

# =============================================================================
# Screen
# =============================================================================

class CodeBox:
    """Specifies a box to contain code. :class:`Screen` uses these to
    determine widget layout, subsequent actions are done within the context of 
    this box. When :func:`CodeBox.build` is called by a :class:`Screen` class
    a widget is built and this box is added to the screen.
    """
    def __init__(self, starting_line_number=-1, auto_scroll=True, height=0, 
            compact=False):
        """Constructor

        :param starting_line_number: -1 means no line numbers, anything larger
                                     will be the first line number displayed.
                                     Defaults to -1
        :param auto_scroll: When True, :class:`purdy.widgets.CodeBox` created
                            by this specification automatically scrolls to
                            newly added content.  Defaults to True.
        :param height: Number of lines the row containing this box should be. 
                       A value of 0 indicates automatic spacing.  Defaults to 0.
        :param compact: if False, the dividing line between this box and the 
                        next has a 1-line empty boundary. Parameter is ignored
                        if there is no item after this one in the rows=[]
                        listing. Defaults to False
        """
        self.height = height
        self.compact = compact
        self.listing = Listing(starting_line_number=starting_line_number)

        self.widget = CodeWidget(self, auto_scroll)

    def build(self, screen, container):
        self.screen = screen
        screen.code_boxes.append(self)

        self.listing.set_display('urwid', self.widget)

        if self.height == 0:
            container.append(self.widget)
        else:
            # height was specified, return a tuple instead
            container.append( (self.height, self.widget) )


class TwinCodeBox:
    """Specifies two side-by-side CodeBoxes. The contained CodeBoxes can be
    either accessed as twin.left and twin.right, or twin[0] and twin[1]. When
    :func:`TwinCodeBox.build` is called, the widgets are created and added to 
    the :attr:`Screen.code_boxes` list sequentially, i.e. a single
    TwinCodeBox results in two CodeBox items in Screen's list.
    """
    def __init__(self, left_starting_line_number=-1, left_auto_scroll=True, 
            left_weight=1, right_starting_line_number=-1, 
            right_auto_scroll=True, right_weight=1, height=0, compact=False):
        """Constructor

        :param left_starting_line_number:
        :param right_starting_line_number: -1 to turn line numbers off, any
                                           higher value is the first number
                                           to display. Defaults to -1

        :param left_auto_scroll:
        :param right_auto_scroll: True to specify that scrolling happens
                                  automatically for the left and right boxes
                                  created by this spec. Defaults to True.

        :param left_weight:
        :param right_weight: relative weights for the widths of the columns,
                             if the values are the same then the columns are
                             the same width, otherwise the widths are formed
                             based on the ratio of left:right. Example:
                             left_weight=2, right_weight=1 means the left side
                             will be twice the width of the right side. Both
                             values default to 1.

        :param height: number of lines for the row this set of boxes is in. 
                       The default of 0 specifies automatic height
        :param compact: if False, the dividing line between this box and the 
                        next has a 1-line empty boundary. Parameter is ignored
                        if there is no item after this one in the rows=[]
                        listing. Defaults to False
        """
        class Side:
            pass

        self.height = height
        self.compact = compact

        left = Side()
        left.weight = left_weight
        left.box = CodeBox(left_starting_line_number, left_auto_scroll)
        self.left = left

        right = Side()
        right.weight = right_weight
        right.box = CodeBox(right_starting_line_number, right_auto_scroll)
        self.right = right

    def build(self, screen, container):
        self.screen = screen

        # use CodeBox's build() method because we need to pack them into Urwid
        # differently
        screen.code_boxes.append(self.left.box)
        self.left.box.listing.set_display('urwid', self.left.box.widget)

        screen.code_boxes.append(self.right.box)
        self.right.box.listing.set_display('urwid', self.right.box.widget)

        # Combine the widgets from the CodeBoxes into a display container
        render_left = ('weight', self.left.weight, self.left.box.widget)
        render_right = ('weight', self.right.weight, self.right.box.widget)

        twin = TwinContainer([render_left, render_right], dividechars=1)

        if self.height != 0:
            twin = (self.height, twin)

        container.append(twin)

    def __getitem__(self, key):
        if key == 0:
            return self.left

        if key == 1:
            return self.right

        raise IndexError


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
    """
    def __init__(self, settings=None, rows=[]):
        self.rows = rows
        self.code_boxes = []
        self.settings = settings
        if settings is None:
            self.settings = default_settings

        self.movie_mode = self.settings['movie_mode']
        if self.movie_mode != -1:
            self.movie_mode = float(self.movie_mode) / 1000.0

        self._build_ui()
        palette = UrwidColourizer.create_palette()
        self.loop = urwid.MainLoop(self.base_window, palette)

        if self.settings['colour'] == 256:
            # don't confuse urwid's screen with ours
            self.loop.screen.set_terminal_properties(colors=256)
            self.loop.screen.reset_default_terminal_palette()

    def _get_args(self):
        if self.settings['deactivate_args']:
            return

        # Screen can be influenced by command line arguments
        parser = argparse.ArgumentParser(description=DESCRIPTION)
        parser.add_argument('--debugsteps', '--ds', action='store_true', 
            help='Print out the animation steps, grouped by Cell and exit')
        self.args = parser.parse_args()

    def _build_ui(self):
        # create a code widget for each box specified in self.rows
        boxen = []

        for index, row in enumerate(self.rows):
            if index != 0:
                # not the first row, add a divider before adding the next box
                compact = self.rows[index - 1].compact
                divider = (3, DividingLine(compact))
                boxen.append(divider)

            row.build(self, boxen)

        self.base_window = BaseWindow(self, boxen)

    def load_actions(self, actions):
        steps = []
        for action in actions:
            steps.extend( action.steps() )

        cells = group_steps_into_cells(steps)
        self.base_window.animation_manager.register(cells)

    def run(self, actions):
        """Calls the main display event loop. Does not return until the UI
        exits."""
        #logger.debug(55*'=')
        self._get_args()
        self.load_actions(actions)

        if hasattr(self, 'args') and self.args.debugsteps:
            for cell in self.base_window.animation_manager.cells:
                print(f'{cell.__class__.__name__}')
                for step in cell.steps:
                    print('   step', step)
            exit()

        # as soon as the loop is going invoke the first animation
        self.loop.set_alarm_in(0, self.base_window.first_alarm)

        # call urwid's main loop, this code doesn't return until the loop
        # exits!!!
        self.loop.run()

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
    """
    def __init__(self, settings=None, top_starting_line_number=-1, 
            top_auto_scroll=True, bottom_starting_line_number=-1,
            bottom_auto_scroll=True, top_height=0):
        self.top = CodeBox(top_starting_line_number, top_auto_scroll, 
            top_height)
        self.bottom = CodeBox(bottom_starting_line_number, bottom_auto_scroll)
        super().__init__(settings, rows=[self.top, self.bottom])


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
    """
    def __init__(self, settings=None, starting_line_number=-1, 
            auto_scroll=True):
        """Foo man chooo"""
        self.code_box = CodeBox(starting_line_number, auto_scroll)
        super().__init__(settings, [self.code_box])

    def thing(self):
        pass
