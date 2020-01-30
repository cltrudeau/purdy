### content.py
#
# Methods for parsing and managing code to be displayed

import os
from collections import namedtuple

from pygments.lexers import PythonConsoleLexer, PythonLexer
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace

# =============================================================================

class LexerContainer:
    def __init__(self):
        self._lexers = {
            'con':(PythonConsoleLexer(), 'Python Console'), 
            'py3':(PythonLexer(), 'Python 3'),
        }

    @property
    def default_name(self):
        return 'con'

    @property
    def choices(self):
        return self._lexers.keys()

    def get_lexer(self, name):
        return self._lexers[name][0]

LEXERS = LexerContainer()
    
# -----------------------------------------------------------------------------

class TokenLookup():
    colours = {
        # urwid colour spec supports both 16 and 256 colour terminals
        #                    fg16            bg16    fg256   bg256
        Token:              ('',             '', '', '',             ''),
        Whitespace:         ('',             '', '', '',             ''),
        Comment:            ('dark cyan',    '', '', 'dark cyan',    ''),
        Comment.Preproc:    ('dark cyan',    '', '', 'dark cyan',    ''),
        Keyword:            ('brown',        '', '', 'brown',        ''),
        Keyword.Type:       ('brown',        '', '', 'brown',        ''),
        Operator:           ('brown',        '', '', 'brown',        ''),
        Operator.Word:      ('brown',        '', '', 'brown',        ''),
        Name:               ('light gray',   '', '', 'light gray',   ''),
        Name.Builtin:       ('dark cyan',    '', '', '#068',         ''),
        Name.Function:      ('dark cyan',    '', '', 'light gray',   ''),
        Name.Namespace:     ('dark cyan',    '', '', 'light gray',   ''),
        Name.Class:         ('dark cyan',    '', '', 'light gray',   ''),
        Name.Exception:     ('dark green',   '', '', 'dark green',   ''),
        Name.Decorator:     ('dark cyan',    '', '', '#66d,bold',    ''),
        Name.Variable:      ('',             '', '', '',             ''),
        Name.Constant:      ('',             '', '', '',             ''),
        Name.Attribute:     ('',             '', '', '',             ''),
        Name.Tag:           ('',             '', '', '',             ''),
        String:             ('dark magenta', '', '', 'dark magenta', ''),
        Number:             ('dark magenta', '', '', 'dark magenta', ''),
        Generic.Prompt:     ('dark blue',    '', '', 'dark blue',    ''),
        Generic.Error:      ('dark green',   '', '', 'dark green',   ''),
        Generic.Traceback:  ('',             '', '', '#a00,bold',    ''),
        Error:              ('dark green',   '', '', '#f00',         ''),
    }

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

    @classmethod
    def get_colour_attribute(cls, token):
        # colour attribute is a 6-tuple, first part being a name (we'll use
        # the same name as the token), next 5 parts are the colour strings for
        # fg16, bg16, x, fg256, bg256
        return ( str(token), ) + tuple( cls.colours[token] )

    @classmethod
    def get_highlight_colour_attribute(cls, token):
        # return 6-tuple colour attribute using the highlight colour as the
        # background colour instead of the one in our table
        colour = cls.colours[token]
        return ( str(token) + '_highlight', 'black', 'light gray', '', 
            'white', 'g23' )

# =============================================================================

CodeToken = namedtuple('CodeToken', ['token_type', 'colour', 'text'])

class CodeBlob:
    def __init__(self, filename, lexer_name):
        filename = os.path.abspath(filename)
        with open(filename) as f:
            contents = f.read()

        lexer = LEXERS.get_lexer(lexer_name)

        self.tokens = []
        for token_type, text in lexer.get_tokens(contents):
            colour = TokenLookup.get_colouring(token_type)
            self.tokens.append( CodeToken(token_type, colour, text) )
