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
