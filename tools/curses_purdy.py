#!/usr/bin/env python

__version__ = '0.1.0'

import time 

import curses

from pygments import highlight
from pygments.lexers import PythonConsoleLexer
from pygments.formatters import Terminal256Formatter, RawTokenFormatter

from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace

# =============================================================================

TYPING_DELAY = 0.130

#token_map = {
#    Token:              ('',            ''),
#
#    Whitespace:         ('gray',   'brightblack'),
#    Comment:            ('gray',   'brightblack'),
#    Comment.Preproc:    ('cyan',        'brightcyan'),
#    Keyword:            ('blue',    'brightblue'),
#    Keyword.Type:       ('cyan',        'brightcyan'),
#    Operator.Word:      ('magenta',      'brightmagenta'),
#    Name.Builtin:       ('cyan',        'brightcyan'),
#    Name.Function:      ('green',   'brightgreen'),
#    Name.Namespace:     ('_cyan_',      '_brightcyan_'),
#    Name.Class:         ('_green_', '_brightgreen_'),
#    Name.Exception:     ('cyan',        'brightcyan'),
#    Name.Decorator:     ('brightblack',    'gray'),
#    Name.Variable:      ('red',     'brightred'),
#    Name.Constant:      ('red',     'brightred'),
#    Name.Attribute:     ('cyan',        'brightcyan'),
#    Name.Tag:           ('brightblue',        'brightblue'),
#    String:             ('yellow',       'yellow'),
#    Number:             ('blue',    'brightblue'),
#
#    Generic.Deleted:    ('brightred',        'brightred'),
#    Generic.Inserted:   ('green',  'brightgreen'),
#    Generic.Heading:    ('**',         '**'),
#    Generic.Subheading: ('*magenta*',   '*brightmagenta*'),
#    Generic.Prompt:     ('**',         '**'),
#    Generic.Error:      ('brightred',        'brightred'),
#
#    Error:              ('_brightred_',      '_brightred_'),
#}

token_map = {
    Token:              'Token',

    Whitespace:         'Whitespace',
    Comment:            'Comment',
    Comment.Preproc:    'Comment.Preproc',
    Keyword:            'Keyword',
    Keyword.Type:       'Keyword.Type',
    Operator.Word:      'Operator.Word',
    Name.Builtin:       'Name.Builtin',
    Name.Function:      'Name.Function',
    Name.Namespace:     'Name.Namespace',
    Name.Class:         'Name.Class',
    Name.Exception:     'Name.Exception',
    Name.Decorator:     'Name.Decorator',
    Name.Variable:      'Name.Variable',
    Name.Constant:      'Name.Constant',
    Name.Attribute:     'Name.Attribute',
    Name.Tag:           'Name.Tag',
    String:             'String',
    Number:             'Number',

    Generic.Deleted:    'Generic.Deleted',
    Generic.Inserted:   'Generic.Inserted',
    Generic.Heading:    'Generic.Heading',
    Generic.Subheading: 'Generic.Subheading',
    Generic.Prompt:     'Generic.Prompt',
    Generic.Error:      'Generic.Error',

    Error:              'Error',
}

TEST = """
>>> numbers = [6, 3, 9, 1]
>>> sorted(numbers)
[1, 3, 6, 9]
"""

TEST2 = """
>>> numbers = [6, 3, 9, 1]
>>>
>>> sorted(numbers)
[1, 3, 6, 9]
>>> numbers
[6, 3, 9, 1]
>>> None < "3"
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: '<' not supported between instances of 'NoneType' and 'str'
>>>
"""

# =============================================================================

class Screen(object):
    """Abstracts away writing text to the curses screen"""
    def __init__(self, win):
        self.win = win
        self.X = 0
        self.Y = 0

    def print(self, text, token=None):
        self.win.addstr(self.Y, self.X, text)
        self.win.refresh()
        self.X += len(text)

        if text.endswith('\n'):
            self.Y += 1
            self.X = 0

# =============================================================================

def map_token(token):
    error = 'Could not map *%s*' % str(token)

    if token in token_map:
        return token_map[token]

    # no match, pull off any children and try again
    parent = token.parent
    while( parent != None ):
        token = token.parent
        if token in token_map:
            return token_map[token]

        parent = token.parent

    # no token map
    raise AttributeError(error)

# -----------------------------------------------------------------------------

def show_code(screen, code):
    lexer = PythonConsoleLexer()

    typewriter = False
    for token, text in lexer.get_tokens(TEST):
        if token == Generic.Prompt:
            screen.print(text)
            typewriter = True

            # wait until the next key press to continue
            curses.flushinp()
            screen.win.getkey()
            continue

        if typewriter:
            for c in text:
                screen.print(c)
                time.sleep(TYPING_DELAY)

            if text == '\n':
                typewriter = False
        else:
            screen.print(text)

# -----------------------------------------------------------------------------

def main(win):
    screen = Screen(win)
    win.clear()

    show_code(screen, TEST)

    # flush anything in the input buffer then wait for a key press to exit
    curses.flushinp()
    win.getkey()

# =============================================================================

curses.wrapper(main)
