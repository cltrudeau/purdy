"""
UI (purdy.ui.py)
----------------

Classes that manage presentation to the screen, the widgets for displaying
code and the event loop for action management are defined in this module

"""

import urwid

from purdy.content import TokenLookup
from purdy.settings import settings as default_settings
from purdy.widgets import CodeBox, DividingLine

# =============================================================================
# Globals

palette = []
highlight_mapper = {}

# =============================================================================
# Main Screen
# =============================================================================

class BaseWindow(urwid.Pile):
    def __init__(self, screen, *args, **kwargs):
        self.screen = screen
        super(BaseWindow, self).__init__(*args, **kwargs)

    def _next_focus(self):
        # switch focus to the next focusable item in our pile

        # want to walk the list of widgets in the pile, starting at the one
        # after the one in focus, looping to the beginning
        #
        # build the list from the focus point to the end, then remove the
        # focus point
        indices = list(range(self.focus_position, len(self.contents)))
        indices.pop(0)

        # add from the beginning of the list to the focus point, inclusive
        indices.extend( range(0, self.focus_position + 1) )

        # now use the list of indicies to find the first widget that is
        # allowed to be focused and focus it
        for index in indices:
            widget, _ = self.contents[index]
            if getattr(widget, 'tab_focusable', False):
                # found a focusable widget, set it as focused and we're done
                self.focus_position = index
                return

    def keypress(self, size, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        if key in ('f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10'):
            # let parent handle function keys
            return super(BaseWindow, self).keypress(size, key)

        if key not in ('right', 'left'):
            # we don't want to pass left/right to the children, we want it to
            # act as "next action", everything else pass to the child to
            # handle for scrolling etc
            result = super(BaseWindow, self).keypress(size, key)
            if result is None:
                # keypress was handled by child, we're done
                return None

        # --- at this point the keypress was not handled by the children, see
        # if we want to do anything with it
        if key == 'tab':
            self._next_focus()
            return None

        if not self.screen.actions:
            # no actions left to do, ignore the keypress
            return None

        if self.screen.movie_mode != -1:
            # in movie mode, ignore key press
            return None

        self.next_action(key)

    def alarm(self, loop, data):
        self.next_action()

    def next_action(self, key=None):
        """Actions are triggered either by a key press or an alarm. This
        method looks in the action queue and gets the tells the top most
        action to take its next step.

        :param key: the key that was pressed, or None if it was an alarm
        """
        try:
            # tell the current action to do its thing
            timer = self.screen.actions[0].next(key)

            if timer != -1:
                # positive value means set callback timer 
                self.screen.loop.set_alarm_in(timer, self.alarm)
            elif self.screen.movie_mode != -1:
                # in movie mode we simulate the key presses, set the callback
                self.screen.loop.set_alarm_in(self.screen.movie_mode, 
                    self.alarm)

        except StopIteration:
            # action is done doing things, pop it off the queue
            self.screen.actions.pop(0)

            if self.screen.actions:
                # there is another action in the action queue, set it up and
                # then force a call back to its first step
                self.screen.actions[0].setup(self.screen.settings)

                if self.screen.movie_mode != -1:
                    # in movie mode we simulate the key presses, set the 
                    # callback
                    self.screen.loop.set_alarm_in(self.screen.movie_mode, 
                        self.alarm)
                else:
                    self.screen.loop.set_alarm_in(0, self.alarm)

# -----------------------------------------------------------------------------

class Screen:
    """Manages the display and event loop for the slide show. All purdy
    scripts need to create one of these or its children.

    This class includes a single :class:`purdy.widgets.CodeBox` widget which 
    can be accessed as :attr:`Screen.code_box`
    """
    def __init__(self, conf_settings=None, show_line_numbers=False,
            auto_scroll=True):
        """Constructor

        :param conf_settings: a settings dictionary object. Defaults to 
                              `None` which uses the default settings
                              dictionary: :attr:`settings.settings`

        :param show_line_numbers: True turns line numbers on inside the
                                  associated code box. Defaults to False
        :param auto_scroll: scroll the :class:`ui.CodeBox` down when new
                            content is added to the bottom. Defaults to True
        """
        self.show_line_numbers = show_line_numbers
        self.settings = conf_settings
        self.auto_scroll = auto_scroll
        if conf_settings is None:
            self.settings = default_settings

        self.movie_mode = self.settings['movie_mode']
        if self.movie_mode != -1:
            self.movie_mode = float(self.movie_mode) / 1000.0

        self._build_boxes()
        self._build_palette()

        self.loop = urwid.MainLoop(self.base_window, palette)

        if self.settings['colour'] == 256:
            self.loop.screen.set_terminal_properties(colors=256)
            self.loop.screen.reset_default_terminal_palette()

    def _build_boxes(self):
        self.code_box = CodeBox(self, self.show_line_numbers, self.auto_scroll)
        self.base_window = BaseWindow(self, [self.code_box, ])

    def _build_palette(self):
        global palette, highlight_mapper

        for token in TokenLookup.colours.keys():
            # add the colour to the palette
            palette.append( TokenLookup.get_colour_attribute(token) )

            # add the highlight version of the colour to the palette
            palette.append( TokenLookup.get_highlight_colour_attribute(token) )

            # add a mapping between the colour and the highlight
            highlight_mapper[str(token)] = str(token) + '_highlight'

        # now append colour attributes that aren't for the tokens
        palette.extend([
            ('line_number', 'dark gray', '', '', 'dark gray', ''),
            ('empty', '', '', '', '', ''),
        ])

        # add default map value
        highlight_mapper[None] = 'highlight'

    def run(self, actions):
        """Calls the main display event loop. Does not return until the UI
        exits."""
        # store our display actions and setup the first one
        self.actions = actions
        self.actions[0].setup(self.settings)

        # as soon as the loop is going invoke the next action, setup a
        # callback
        if self.movie_mode != -1:
            # in movie mode we simulate the key presses, set the callback to
            # start the process
            self.loop.set_alarm_in(self.movie_mode, self.base_window.alarm)
        else:
            self.loop.set_alarm_in(0, self.base_window.alarm)

        # call urwid's main loop, this code doesn't return until the loop
        # exits!!!
        self.loop.run()

# -----------------------------------------------------------------------------

class SplitScreen(Screen):
    """Inheritor of :class:`Screen`. This implementation supports two 
    :class:`CodeBox` instances, stacked vertically and separated by a dividing
    line. The code boxes are :attr:`SplitScreen.top_box` and
    :attr:`SplitScreen.bottom_box`. 
    """
    def __init__(self, conf_settings=None, show_top_line_numbers=False,
            top_auto_scroll=True, show_bottom_line_numbers=False, 
            bottom_auto_scroll=True, top_height=0):
        """Constructor

        :param conf_settings: a settings dictionary object. Defaults to 
                              `None` which uses the default settings
                              dictionary: :attr:`settings.settings`

        :param show_top_line_numbers: True turns line numbers on inside the
                                      top code box. Defaults to False
        :param top_auto_scroll: When True, the top :class:`ui.CodeBox` 
                                automatically scrolls to newly added content.
                                Defaults to True.
        :param show_bottom_line_numbers: True turns line numbers on inside the
                                         bottom code box. Defaults to False
        :param bottom_auto_scroll: When True, the bottom :class:`ui.CodeBox` 
                                automatically scrolls to newly added content.
                                Defaults to True.
        :param top_height: Number of lines the top box should be. A value of 0
                           indicates top and bottom should be the same size.
                           Defaults to 0.
        """
        self.show_top_line_numbers = show_top_line_numbers
        self.top_auto_scroll = top_auto_scroll
        self.show_bottom_line_numbers = show_bottom_line_numbers
        self.bottom_auto_scroll = bottom_auto_scroll
        self.top_height = top_height
        super().__init__(conf_settings)

    def _build_boxes(self):
        # override the default build, creating two code boxes instead
        self.top_box = CodeBox(self, self.show_top_line_numbers,
            self.top_auto_scroll)
        divider = (3, DividingLine())
        self.bottom_box = CodeBox(self, self.show_bottom_line_numbers, 
            self.bottom_auto_scroll)

        first_box = self.top_box
        if self.top_height != 0:
            first_box = (self.top_height, self.top_box)

        self.base_window = BaseWindow(self, [first_box, divider,
            self.bottom_box])

# =============================================================================
# GridScreen
# =============================================================================

class Box:
    """Specifies a box to contain code, used by :class:`RowScreen`"""
    def __init__(self, line_numbers=False, auto_scroll=True, height=0):
        """Constructor

        :param line_numbers: True turns line numbers on inside the 
                             :class:`purdy.widgets.CodeBox` created by this
                             specification. Defaults to False
        :param auto_scroll: When True, :class:`purdy.widgets.CodeBox` created
                            by this specification automatically scrolls to
                            newly added content.  Defaults to True.
        :param height: Number of lines the row containing this box should be. 
                       A value of 0 indicates automatic spacing.  Defaults to 0.
        """
        self.line_numbers = line_numbers
        self.auto_scroll = auto_scroll
        self.height = height

    def build(self, screen, container):
        codebox = CodeBox(self, self.line_numbers, self.auto_scroll)
        screen.code_boxes.append(codebox)
        if self.height != 0:
            codebox = (self.height, codebox)

        container.append(codebox)


class TwinBox:
    """Specifies two side-by-side boxes to contain code, used by 
    :class:`RowScreen`
    """
    def __init__(self, left_line_numbers=False, left_auto_scroll=True, 
        right_line_numbers=False, right_auto_scroll=True, height=0):
        """Constructor

        :param left_line_numbers:
        :param right_line_numbers: True to show line numbers in the left and
                                   right box created by this spec. Defaults to
                                   False
        :param left_auto_scroll:
        :param right_auto_scroll: True to specify that scrolling happens
                                  automatically for the left and right boxes
                                  created by this spec. Defaults to True.
        :param height: number of lines for the row this set of boxes is in. 
                       The default of 0 specifies automatic height
        """
        self.left_line_numbers = left_line_numbers
        self.left_auto_scroll = left_auto_scroll
        self.right_line_numbers = right_line_numbers
        self.right_auto_scroll = right_auto_scroll
        self.height = height

    def build(self, screen, container):
        left = CodeBox(self, self.left_line_numbers, self.left_auto_scroll)
        screen.code_boxes.append(left)
        right = CodeBox(self, self.right_line_numbers, self.right_auto_scroll)
        screen.code_boxes.append(right)

        pad = urwid.Padding(left, right=1)

        column = urwid.Columns([pad, right])

        if self.height != 0:
            column = (self.height, column)

        container.append(column)


class RowScreen(Screen):
    """Inheritor of :class:`Screen`. This implementation supports
    specification of multiple rows of
    :class:`purdy.widgets.CodeBox` objects.

    """
    def __init__(self, conf_settings=None, rows=[]):
        """Constructor

        :param conf_settings: a settings dictionary object. Defaults to 
                              `None` which uses the default settings
                              dictionary: :attr:`settings.settings`

        :param rows: a list containing one or more :class:`Box` or 
                     :class:`TwinBox` definitions, to specify the layout of the
                     screen
        """
        self.rows = rows
        self.code_boxes = []
        super().__init__(conf_settings)

    def _build_boxes(self):
        # override the default build, creating a code box for each specified
        boxen = []

        for index, row in enumerate(self.rows):
            if index != 0:
                # not the first row, add a divider before adding the next box
                divider = (3, DividingLine())
                boxen.append(divider)

            row.build(self, boxen)

        self.base_window = BaseWindow(self, boxen)
