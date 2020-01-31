### content.py
#
# Methods for parsing and managing code to be displayed

import os
from collections import namedtuple
from copy import copy
from enum import Enum

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
    def is_a(cls, token1, token2):
        ### Returns true if token1 is equal to or a child of token2
        if token1 == token2:
            return True

        parent = token1.parent
        while(parent != None):
            if parent == token2:
                return True

            parent = parent.parent

        return False

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
        return ( str(token) + '_highlight', 'black', 'light gray', '', 
            'white', 'g23' )

    @classmethod
    def line_number_markup(cls, line_number):
        return ('line_number', f'{line_number:3} ')

# =============================================================================

CodeToken = namedtuple('CodeToken', ['token_type', 'colour', 'text'])

class Animate(Enum):
    WAIT = 0
    DELAY = 1
    NEWLINE = 2


class CodeLine:
    def __init__(self, tokens):
        self.tokens = tokens
        self.markup = ['']
        self.is_output = self.tokens[0] == Generic.Output

        for token in self.tokens:
            if token.text == '':
                # tokenizer sometimes puts in empty stuff, skip it
                continue
            else:
                # append markup tuple to end of last row
                markup_tuple = (token.colour, token.text)
                if self.markup == ['']:
                    # was empty line, replace it with new markup
                    self.markup = [markup_tuple, ]
                else:
                    self.markup.append(markup_tuple)


class Code:
    def __init__(self, contents, lexer_name, show_line_numbers=False):
        self.show_line_numbers = show_line_numbers
        lexer = LEXERS.get_lexer(lexer_name)

        # parse the code
        self.tokens = []
        for token_type, text in lexer.get_tokens(contents):
            colour = TokenLookup.get_colouring(token_type)
            self.tokens.append( CodeToken(token_type, colour, text) )

        # turn our tokens into lines of code
        self._build_code_lines()

    def _build_code_lines(self):
        self.lines = []

        token_set = []
        for token in self.tokens:
            if token.text == '\n':
                # hit a CR, time to create a new CodeLine object
                if not token_set:
                    token2 = CodeToken(token.token_type, 'empty', '')
                    token_set = [token2 ]

                line = CodeLine(token_set)
                self.lines.append(line)

                # reset to start the next group of tokens
                token_set = []
            elif token.text == '':
                # tokenizer sometimes puts in empty stuff, skip it
                continue
            elif TokenLookup.is_a(token.token_type, String) and \
                    '\n' in token.text:
                # String tokens may be multi-line
                for row in token.text.split('\n'):
                    token2 = CodeToken(token.token_type, token.colour, 
                        row)
                    token_set.append(token2)
                    line = CodeLine( token_set )
                    self.lines.append(line)

                    token_set = []
            else:
                if token.text[-1] == '\n':
                    # there is a \n at the end of the token, need to rebuild
                    # it without it, then create the CodeLine object
                    token2 = CodeToken(token.token_type, token.colour,
                        token.text.rstrip('\n'))
                    token_set.append(token2)

                    # token text caused a CR, create a new CodeLine object
                    line = CodeLine(token_set)
                    self.lines.append(line)

                    # reset to start the next group of tokens
                    token_set = []
                else:
                    token_set.append(token)

    def typewriter_chunks(self):
        return TypewriterChunkifier().parse(self.tokens)

# -----------------------------------------------------------------------------

class CodeFile(Code):
    def __init__(self, filename, lexer_name):
        filename = os.path.abspath(filename)
        with open(filename) as f:
            contents = f.read()

        super().__init__(contents, lexer_name)

# -----------------------------------------------------------------------------

class TypewriterChunkifier:
    ### Encapsulates token parsing into typewriter animation chunks

    def __init__(self):
        self.chunks = []
        self.line = []
        self.traceback = False

        self.handlers = {
            Generic.Prompt   :self._prompt_handler,
            Generic.Output   :self._output_handler,
            Generic.Traceback:self._traceback_handler,
        }

    def _prompt_handler(self, token):
        ### chunkifies Generic.Prompt tokens
        if self.traceback:
            # we're in traceback mode, spit out the last line then get
            # out of traceback mode
            self.traceback = False
            if self.line:
                self.chunks.append( copy(self.line) )
                self.line = []
        
        markup = (token.colour, token.text)
        self.line.append(markup)
        self.chunks.append( copy(self.line) )
        self.chunks.append( Animate.WAIT )

    def _output_handler(self, token):
        ### chunkifies Generic.Output tokens
        for row in token.text.rstrip('\n').split('\n'):
            self.chunks.append( (token.colour, row) )
            self.chunks.append( Animate.NEWLINE )

    def _traceback_handler(self, token):
        ### chunkifies Generic.Traceback tokens

        # tracebacks are funny, they are followed by stack trace information
        # that should be colourized but treated as a single output block, go
        # into "traceback mode" so that no animation happens until we get to
        # the next Prompt
        self.traceback = True
        text = token.text.rstrip()
        if text:
            self.chunks.append( (token.colour, token.text.rstrip() ) )
            self.chunks.append( Animate.NEWLINE )

        self.line = []

    def _default_handler(self, token):
        ### chunkifies tokens without specific handlers
        if self.traceback:
            self.line.append( (token.colour, token.text) )
        else:
            # type things letter by letter now
            word = ''
            for letter in token.text:
                word += letter
                markup = (token.colour, word)

                if len(word) == 1:
                    self.line.append( markup )
                else:
                    self.line[-1] = markup

                self.chunks.append( copy(self.line) )
                self.chunks.append( Animate.DELAY )

    def parse(self, tokens):
        for token in tokens:
            if token.text == '' and token.token_type != Generic.Traceback:
                # skip empty tokens
                continue

            if token.text == '\n':
                if self.line:
                    self.chunks.append( copy(self.line) )
                    self.line = []

                self.chunks.append( Animate.NEWLINE )
                continue

            # lookup the handler for this token and run it
            fn = self.handlers.get(token.token_type, self._default_handler)
            fn(token)

        # clean off any instructions from the end (e.g. if it ends in a Prompt
        # there will be a WAIT and a NEWLINE
        while isinstance(self.chunks[-1], Animate):
            self.chunks.pop()

        return self.chunks
