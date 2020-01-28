import urwid

from purdy.content import TokenLookup
from purdy.settings import settings as default_settings

# =============================================================================
# Main Screen
# =============================================================================

class BaseWindow(urwid.Pile):
    def __init__(self, screen, *args, **kwargs):
        self.screen = screen
        super(BaseWindow, self).__init__(*args, **kwargs)

    def keypress(self, size, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        result = super(BaseWindow, self).keypress(size, key)
        if result is None:
            # keypress was handled by child, we're done
            return None

        # --- at this point the keypress was not handled by the children, see
        # if we want to do anything with it

        if key == 'tab':
            # switch focus to the next focusable item in our pile

            # want to walk the list of widgets in the pile, starting at the
            # one after the one in focus, looping to the beginning
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
                    # found a focusable widget, set it as focused and we're
                    # done
                    self.focus_position = index
                    break

            return None

        if not self.screen.actions:
            # no actions left to do, ignore the keypress
            return None

        if self.screen.settings['movie_mode'] != -1:
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
                # there is another action in the action queue, set it up
                self.screen.actions[0].setup(self.screen.settings)

                if self.screen.movie_mode != -1:
                    # in movie mode we simulate the key presses, set the 
                    # callback
                    self.screen.loop.set_alarm_in(self.screen.movie_mode, 
                        self.alarm)


class Screen:
    def __init__(self, conf_settings=None):
        self.settings = conf_settings
        if conf_settings is None:
            self.settings = default_settings

        self.movie_mode = self.settings['movie_mode']
        if self.movie_mode != -1:
            self.movie_mode = float(self.movie_mode) / 1000.0

        self._build_boxes()
        self.loop = urwid.MainLoop(self.base_window, TokenLookup.palette)

    def _build_boxes(self):
        self.code_box = CodeListBox()
        self.base_window = BaseWindow(self, [self.code_box, ])

    def run(self, actions):
        """Calls the main event loop in urwid. Does not return until the UI
        exits."""
        # store our display actions and setup the first one
        self.actions = actions
        self.actions[0].setup(self.settings)

        if self.movie_mode != -1:
            # in movie mode we simulate the key presses, set the callback to
            # start the process
            self.loop.set_alarm_in(self.movie_mode, self.base_window.alarm)

        # call urwid's main loop, this code doesn't return until the loop
        # exits!!!
        self.loop.run()


class SplitScreen(Screen):
    def _build_boxes(self):
        # override the default build, creating two code boxes instead
        self.top_box = CodeBox()
        #self.top_box = CodeListBox()
        divider = (3, DividingLine())

        #self.bottom_box = CodeListBox()
        self.bottom_box = CodeBox()

        self.base_window = BaseWindow(self, [self.top_box, divider,
            self.bottom_box])

# =============================================================================
# Widgets
# =============================================================================

class AppendableText(urwid.Text):
    def append(self, markup):
        text, attrs = self.get_text()
        output = []
        if len(attrs) == 0:
            # no attributes, just add the text
            output.append((None, text))
        else:
            # have attributes, get_text() returns a string and a series of
            # tuples that are the name of the attribute applied and the
            # length, need to re-build the list of text pieces for set_text()
            #import pudb; pudb.set_trace()
            pos = 0
            for name, length in attrs:
                if length == 0:
                    # empty strings mess up urwid's attributes, skip them if
                    # they happend
                    continue

                text_piece = text[pos:pos+length]
                pos += length
                output.append( (name, text_piece) )

            if pos < len(text):
                output.append( (None, text[pos:]) )

        # now we actually want to append something
        if isinstance(markup, list):
            output.extend(markup)
        elif isinstance(markup, tuple):
            output.append(markup)
        else:
            # not a list, not a tuple, must be a string; tack it on the end of
            # the output with no attributes
            output.append( (None, markup) )

        self.set_text(output)

# -----------------------------------------------------------------------------

class DividingLine(urwid.Filler):
    tab_focusable = False

    def __init__(self):
        divider = urwid.Divider('-')
        super(DividingLine, self).__init__(divider, valign='top', top=1, 
            bottom=1)


class CodeListBox(urwid.ListBox):
    tab_focusable = True

    def __init__(self):
        self.body = urwid.SimpleListWalker([AppendableText('')])
        super(CodeListBox, self).__init__(self.body)

    def append_newline(self):
        # add a new line to our listbox
        self.body.contents.append(AppendableText(''))

    def append_token(self, colour, text):
        # add a coloured token to the last line of our list
        self.body.contents[-1].append( (colour, text) )

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
    tab_focusable = True

    # CodeBox is ListBox of Text with code in it accompanied by a side bar
    # with indicators about focus and scroll position
    def __init__(self):
        self.body = urwid.SimpleListWalker([AppendableText('')])

        scroller = ScrollingIndicator()
        listbox = ScrollingListBox(scroller, self.body)

        layout = [listbox, (1, scroller)]

        super(CodeBox, self).__init__(layout)

    def append_newline(self):
        # add a new line to our listbox
        self.body.contents.append(AppendableText(''))

    def append_token(self, colour, text):
        # add a coloured token to the last line of our list
        self.body.contents[-1].append( (colour, text) )
