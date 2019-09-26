#!/usr/bin/env python

__version__ = '0.1.0'

import argparse
from enum import Enum
import time 

from pygments import highlight
from pygments.lexers import PythonConsoleLexer
from pygments.formatters import Terminal256Formatter, RawTokenFormatter

from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace

import urwid

# =============================================================================

TYPING_DELAY = 0.130

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
    WAITING = 0
    TYPING  = 1


class CodeListBox(urwid.ListBox):
    def __init__(self, code):
        self.body = urwid.SimpleListWalker([AppendableText('')])
        self.state = State.WAITING

        # parse and store the pygment'd code
        lexer = PythonConsoleLexer()
        self.code_tokens = list(lexer.get_tokens(code))
        self.code_index = 0
        self.code_len = len(self.code_tokens)

        super(CodeListBox, self).__init__(self.body)

    def keypress(self, size, key):
        key = super(CodeListBox, self).keypress(size, key)

        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        # if we've output all the code, ignore the keypress
        if self.code_index >= self.code_len:
            return

        if self.state == State.WAITING:
            # loop through our code until we hit a prompt or a "\n"

            for token, text in self.code_tokens[self.code_index:]:
                self.code_index += 1
                colour = TokenLookup.get_colouring(token)

                #if token == Generic.Prompt:
                #    # in case of a prompt, print it and then wait for next
                #    # keypress
                #    self.body.contents[-1].append(text)
                #    break

                if text == '\n':
                    # hit a CR, add a new line to our output
                    self.body.contents.append(AppendableText(''))
                else:
                    # just append whatever we have
                    self.body.contents[-1].append( (colour, text) )

            #import pudb; pudb.set_trace()

# =============================================================================
# Main
# =============================================================================

# define command line arguments
parser = argparse.ArgumentParser(description=('Displays a highlighted version '
    'of python text to the screen as if it is being typed'))
parser.add_argument('files', type=str, nargs='+',
    help='One or more file names to parse')
args = parser.parse_args()

# get file contents and use urwid to display
with open(args.files[0]) as f:
    contents = f.read()

box = CodeListBox(contents)
loop = urwid.MainLoop(box, TokenLookup.palette)
#loop.set_alarm_in(1, do_append)
loop.run()
