import urwid

from purdy.content import TokenLookup
from purdy.settings import settings as default_settings

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


class Screen:
    """Manages the display and event loop for the slide show. All purdy
    scripts need to create one of these or its children.

    This class includes a single :class:`ui.CodeBox` widget which can be accessed
    as :attr:`Screen.code_box`
    """
    def __init__(self, conf_settings=None, show_line_numbers=False):
        """Constructor

        :param conf_settings: a settings dictionary object. Defaults to 
                              `None` which uses the default settings
                              dictionary: :attr:`settings.settings`

        :param show_line_numbers: True turns line numbers on inside the
                                  associated code box. Defaults to False
        """
        self.show_line_numbers = show_line_numbers
        self.settings = conf_settings
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
        self.code_box = CodeBox(self, self.show_line_numbers)
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


class SplitScreen(Screen):
    """Inheritor of :class:`Screen`. This implementation supports two 
    :class:`CodeBox` instances, stacked vertically and separated by a dividing
    line. The code boxes are :attr:`SplitScreen.top_box` and
    :attr:`SplitScreen.bottom_box`. 
    """
    def __init__(self, conf_settings=None, show_top_line_numbers=False,
            show_bottom_line_numbers=False):
        """Constructor

        :param conf_settings: a settings dictionary object. Defaults to 
                              `None` which uses the default settings
                              dictionary: :attr:`settings.settings`

        :param show_line_numbers: True turns line numbers on inside the
                                  associated code box. Defaults to False
        """
        self.show_top_line_numbers = show_top_line_numbers
        self.show_bottom_line_numbers = show_bottom_line_numbers
        super().__init__(conf_settings)

    def _build_boxes(self):
        # override the default build, creating two code boxes instead
        self.top_box = CodeBox(self, self.show_top_line_numbers)
        divider = (3, DividingLine())
        self.bottom_box = CodeBox(self, self.show_bottom_line_numbers)

        self.base_window = BaseWindow(self, [self.top_box, divider,
            self.bottom_box])

# =============================================================================
# Widgets
# =============================================================================

class AppendableText(urwid.AttrMap):
    ### Text-like widget that supports highlighting

    def __init__(self, markup):
        self.text_widget = urwid.Text('')
        self.set_text(markup)
        super(AppendableText, self).__init__(self.text_widget, 'empty')

    def set_text(self, markup):
        # urwid.Text supports three formats for markup: 1) plain text, 2)
        # tuple of palette attribute name and text, or 3) a list contain items
        # which are #1 or #2; to make things easier, convert it to a list
        self.markup = markup
        if isinstance(markup, str) or isinstance(markup, tuple):
            self.markup = [markup]

        self.text_widget.set_text(self.markup)

    def append(self, markup):
        self.markup.append(markup)
        self.set_text(self.markup)

    def set_highlight(self, highlight):
        if highlight:
            global highlight_mapper
            self.set_attr_map(highlight_mapper)
        else:
            self.set_attr_map({})

# -----------------------------------------------------------------------------

class DividingLine(urwid.Filler):
    tab_focusable = False

    def __init__(self):
        divider = urwid.Divider('-')
        super(DividingLine, self).__init__(divider, valign='top', top=1, 
            bottom=1)

# -----------------------------------------------------------------------------
# Code Box -- box that displays code

class ScrollingIndicator(urwid.Frame):
    def __init__(self):
        self.up = urwid.Text(' ')
        self.down = urwid.Text(' ')

        # create this Frame with a solid fill in the middle and the up and
        # down Text widgets as the header and footer
        super(ScrollingIndicator, self).__init__(urwid.SolidFill(' '), 
            header=self.up, footer=self.down)

    def set_up(self, is_up, focus):
        if is_up and focus:
            self.up.set_text('▲')
        elif is_up and not focus:
            self.up.set_text('△')
        else:
            self.up.set_text(' ')

    def set_down(self, is_down, focus):
        if is_down and focus:
            self.down.set_text('▼')
        elif is_down and not focus:
            self.down.set_text('▽')
        else:
            self.down.set_text(' ')


class ScrollingListBox(urwid.ListBox):
    def __init__(self, scroll_indicator, *args, **kwargs):
        self.scroll_indicator = scroll_indicator
        super(ScrollingListBox, self).__init__(*args, **kwargs)

    def render(self, size, focus):
        result = super(ScrollingListBox, self).render(size, focus)

        # ends_visible() returns a list with the words "top" and/or "bottom"
        # in it if the top and/or bottom of the list box is visible
        #
        # set our scrolling indicators based on what is visible
        visible = self.ends_visible(size)
        self.scroll_indicator.set_up('top' not in visible, focus)
        self.scroll_indicator.set_down('bottom' not in visible, focus)

        return result


class CodeBox(urwid.Columns):
    """Widget that displays the code. Actions use the methods in this class to
    change the text being displayed.

    The widget wraps an urwid ListBox, with each line in the box being a line
    of code. It also provides indiciators on the right side of the screen as
    to whether there is content above or below the current screen. If the
    parent :class:`Screen` implementation has multiple instances of this class
    active, the scroll area will also indicate which code box is focused. 

    The up and down arrows as well as the page-up and page-down buttons are
    supported. If there are multiple code boxes, tab key will change the
    focus.

    Each line of the code box displays text through the :class:`urwid.Text`
    widget. The methods in the this class for displaying content use urwid's
    markup tuple for determing the appearance of text. If you are writing new
    actions, you generally don't need to understand the markup language, just
    pass in the :class:`CodeLine.markup <purdy.content.CodeLine>` 
    attribute from the line in your :class:`Code <purdy.content.Code>` object.
    """
    tab_focusable = True

    # CodeBox is ListBox of Text with code in it accompanied by a side bar
    # with indicators about focus and scroll position
    def __init__(self, screen, show_line_numbers):
        """Constructor. These objects should only be constructed by a parent
        :class:`Screen` object.

        :param screen: the :class:`Screen` building this code box

        :param show_line_numbers: True if this box is to display line numbers
        """
        self.screen = screen
        self.show_line_numbers = show_line_numbers
        self.line_number = 1
        self.body = urwid.SimpleListWalker([])

        scroller = ScrollingIndicator()
        listbox = ScrollingListBox(scroller, self.body)

        layout = [listbox, (1, scroller)]

        super(CodeBox, self).__init__(layout)

    def clear(self):
        # clears the list and starts fresh
        self.body.contents.clear() 

    # --- Add Lines
    def add_line(self, markup=['']):
        """Appends an empty line to the end of the code listing

        :param markup: markup to put in the line, defaults to empty
        """
        self.add_line_at(len(self.body.contents) + 1, markup)

    def add_line_at(self, position, markup=['']):
        """Inserts a new empty line in the code box

        :param position: line number to insert at (1-indexed), pushes any
            existing content down; i.e. position=1 inserts at the top of the
            list
        :param markup: markup to put in the newly inserted line, defaults to
                       empty
        """
        if self.show_line_numbers:
            markup = [TokenLookup.line_number_markup(position), ] +  markup

        self.body.contents.insert(position - 1, AppendableText(markup))

    def fix_line_numbers(self, position):
        """Fixes line numbers after adding new lines to the code box"""
        line_no = position
        for widget in self.body.contents[line_no - 1:]:
            markup = widget.markup

            # this should only be called in show_line_numbers mode, so we can
            # assume that the first part of the markup is the line number
            # chunk
            #
            # re-build the markup, replacing the line number chunk with a new
            # one
            text = TokenLookup.line_number_markup(line_no)
            new_markup = [text, ] + markup[1:]
            widget.set_text(new_markup)

            line_no += 1

    # --- Set line
    def set_last_line(self, markup):
        """Changes the last line in the code box to have the given markup 

        :param markup: new markup tuple for the line
        """
        self.body.contents[-1].set_text(markup)

    def set_line(self, position, markup):
        """Changes the given line in the code box to have the given markup 

        :param position: line number to change (1-indexed)
        :param markup: new markup tuple for the line
        """
        self.body.contents[position - 1].set_text(markup)
