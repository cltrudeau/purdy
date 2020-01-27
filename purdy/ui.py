import random
from enum import Enum

from pygments.lexers import PythonConsoleLexer
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace

import urwid

# =============================================================================
# Utility Classes
# =============================================================================

class TokenLookup():
    colours = {
        Token:              ('',             ''),
        Whitespace:         ('',             ''),
        Comment:            ('dark cyan',    ''),
        Comment.Preproc:    ('dark cyan',    ''),
        Keyword:            ('brown',       ''),
        Keyword.Type:       ('brown',       ''),
        Operator.Word:      ('brown',       ''),
        Name.Builtin:       ('dark cyan',    ''),
        Name.Function:      ('dark cyan',    ''),
        Name.Namespace:     ('dark cyan',    ''),
        Name.Class:         ('dark cyan',    ''),
        Name.Exception:     ('dark green',   ''),
        Name.Decorator:     ('dark cyan',    ''),
        Name.Variable:      ('',             ''),
        Name.Constant:      ('',             ''),
        Name.Attribute:     ('',             ''),
        Name.Tag:           ('',             ''),
        String:             ('dark magenta', ''),
        Number:             ('dark magenta', ''),
        Generic.Prompt:     ('dark blue',    ''),
        Generic.Error:      ('dark green',   ''),
        Error:              ('dark green',   ''),
    }

    palette = None

    @classmethod
    def get_colouring(cls, token):
        # Tokens are hierarchical and mapped to colours in our palette using
        # their names. If the token is in our colour map, return its name, if
        # it isn't, go up its hierarchy until a match is found
        if token in cls.colours:
            return str(token)

        # token not in our map, search its ancestors
        token = token.parent
        while(token != None):
            if token in cls.colours:
                return str(token)

            token = token.parent

        # something went wrong with our lookup, return the default
        return 'Token'


# can't do a list comprehension in the declarative area of the class, due to
# scoping rules, do it here
TokenLookup.palette = [(str(token), colour[0], colour[1]) for token, colour in \
    TokenLookup.colours.items()]

# -----------------------------------------------------------------------------
# Widgets
# -----------------------------------------------------------------------------

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


class State(Enum):
    CONTINUOUS = 0

    WAITING = 1
    ABOUT_TO_TYPE = 2
    TYPING  = 2


class CodeListBox(urwid.ListBox):
    def __init__(self, typing_delay, variance, state):
        self.body = urwid.SimpleListWalker([AppendableText('')])
        self.state = state
        self.typing_delay = typing_delay
        self.variance = variance

        super(CodeListBox, self).__init__(self.body)

    def setup(self, loop, code):
        # call this method once the main loop has been created
        self.loop = loop

        # parse and store the pygment'd code
        lexer = PythonConsoleLexer()
        self.code_tokens = list(lexer.get_tokens(code))
        self.code_index = 0
        self.code_len = len(self.code_tokens)
        self.typing = []
        self.typing_token = None

        if self.state == State.CONTINUOUS:
            self.show_tokens()
        else:
            self.show_tokens(Generic.Prompt)
            self.state = State.ABOUT_TO_TYPE

    def show_tokens(self, stop_after=None):
        """Adds colourized contents to our list box. If "stop_after" is given, 
        it returns after adding the token of the given type
        """
        for token, text in self.code_tokens[self.code_index:]:
            self.code_index += 1
            colour = TokenLookup.get_colouring(token)

            if text == '\n':
                # hit a CR, add a new line to our output
                self.body.contents.append(AppendableText(''))
            else:
                # just append whatever we have
                self.body.contents[-1].append( (colour, text) )

            if token == stop_after:
                break

    def typewriter(self, loop=None, data=None):
        if self.typing == []:
            # nothing in queue, start typing the next token
            token, text = self.code_tokens[self.code_index]
            colour = TokenLookup.get_colouring(token)
            self.code_index += 1

            if text == '\n':
                # hit a CR, add a new line to our output, leave typewrite,
                # print tokens until next prompt
                self.body.contents.append(AppendableText(''))
                self.show_tokens(stop_after=Generic.Prompt)
                self.state = State.ABOUT_TO_TYPE
                return
            elif text == '':
                # lexer spits out empty text sometimes, need to ignore it
                self.loop.set_alarm_in(0, self.typewriter)
            else:
                # insert first letter into our text widget, keep the rest
                # and set a timer for the next letter
                self.body.contents[-1].append( (colour, text[0]) )
                self.typing = list(text[1:])
                self.typing_token = token

                vary_by = random.randint(0, 2 * self.variance) - self.variance
                delay = self.typing_delay + (vary_by / 1000)
                self.loop.set_alarm_in(delay, self.typewriter)
        else:
            # get the next letter off the typing queue and add it to our
            # widget
            colour = TokenLookup.get_colouring(self.typing_token)
            letter = self.typing.pop(0)
            self.body.contents[-1].append( (colour, letter) )
            self.loop.set_alarm_in(self.typing_delay, self.typewriter)

    def keypress(self, size, key):
        key = super(CodeListBox, self).keypress(size, key)

        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        # if we've output all the code, ignore the keypress
        if self.code_index >= self.code_len:
            return

        # you should only get here if we are not in CONTINUOUS mode
        if self.state == State.WAITING:
            # want to stop after we see a prompt
            self.show_tokens(stop_after=Generic.Prompt)

            # after we printed the prompt we want to go into typewriter mode,
            # set the state and wait for the next keypress
            self.state = State.ABOUT_TO_TYPE
        elif self.state == State.ABOUT_TO_TYPE:
            # got the keypress while waiting to type, start typing
            self.state = State.TYPING
            self.typewriter()

        # else: State.TYPING, ignore keypress

# =============================================================================
# Window Runner
# =============================================================================

def purdy_window(delay, variance, state, contents):
    """Launches the urwid window loop showing the given contents. Does not
    return until the urwid loop exits."""

    box = CodeListBox(delay, variance, state)
    loop = urwid.MainLoop(box, TokenLookup.palette)
    box.setup(loop, contents)
    loop.run()
