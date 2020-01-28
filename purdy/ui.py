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

        if not self.screen.actions:
            # no actions left to do, ignore the keypress
            return

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

        except StopIteration:
            # action is done doing things, pop it off the queue
            self.screen.actions.pop()


class Screen:
    def __init__(self, conf_settings=None):
        self.settings = conf_settings
        if conf_settings is None:
            self.settings = default_settings

        self.code_box = CodeListBox(conf_settings)
        base_window = BaseWindow(self, [self.code_box, ])

        self.loop = urwid.MainLoop(base_window, TokenLookup.palette)

    def run(self, actions):
        """Calls the main event loop in urwid. Does not return until the UI
        exits."""
        # store our display actions and setup the first one
        self.actions = actions
        self.actions[0].setup(self.settings)

        # call urwid's main loop
        self.loop.run()

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


class CodeListBox(urwid.ListBox):
    def __init__(self, settings):
        self.body = urwid.SimpleListWalker([AppendableText('')])
        super(CodeListBox, self).__init__(self.body)

    def append_newline(self):
        # add a new line to our listbox
        self.body.contents.append(AppendableText(''))

    def append_token(self, colour, text):
        # add a coloured token to the last line of our list
        self.body.contents[-1].append( (colour, text) )
