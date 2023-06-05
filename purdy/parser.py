"""
Parser
======

This contains methods and classes to manage parsing of code
"""

from copy import deepcopy
from collections import namedtuple

from pygments.lexers import (PythonConsoleLexer, PythonLexer, BashSessionLexer,
    NodeConsoleLexer)
from pygments.lexers.data import YamlLexer
from pygments.lexers.markup import MarkdownLexer, RstLexer
from pygments.token import String, Token

from purdy.lexers import DollarBashSessionLexer, NewlineLexer

# =============================================================================
# Pygments Token Management
# =============================================================================

class PurdyLexer:
    """Container for the built-in supported lexers. This class is where the
    names of the lexers are defined. Current choices are:

    * 'con' -- Python 3 Console
    * 'py3' -- Python 3 Source code
    * 'bash' -- interactive Bash session
    * 'dbash' -- interactive Bash session using a dollar sign prompt
    * 'node' -- interactive JavaScript / Node.js session
    * 'yaml' -- YAML document
    * 'rst' -- RST document
    * 'md' -- Markdown document
    * 'none' -- Use plain text, no lexing
    """

    _registry = {
        'con':('con', 'Python 3 Console', PythonConsoleLexer, True, 'code'),
        'py3':('py3', 'Python 3 Source', PythonLexer, False, 'code'),
        'bash':('bash', 'Bash Console', BashSessionLexer, True, 'code'),
        'dbash':('dbash', 'Bash Console with a dollar-sign prompt',
            DollarBashSessionLexer, True, 'code'),
        'node':('node', 'JavaScript Node.js Console', NodeConsoleLexer, True,
            'code'),
        'yaml':('yaml', 'YAML Doc', YamlLexer, False, 'doc'),
        'rst':('rst', 'RST Doc', RstLexer, False, 'doc'),
        'md':('md', 'Markdown Doc', MarkdownLexer, False, 'doc'),
        'none':('none', 'No Parsing', NewlineLexer, False, 'doc'),
    }

    def __init__(self, name, description, pygments_lexer_cls, is_console,
            palette):
        self.name = name
        self.description = description
        self.pygments_lexer = pygments_lexer_cls()
        self.is_console = is_console
        self.palette = palette

    @classmethod
    def factory_from_source(cls, source):
        if source.startswith('>>> ') or '\n>>> ' in source:
            return PurdyLexer(*cls._registry['con'])
        elif source.startswith('$ ') or '\n$ ' in source:
            return PurdyLexer(*cls._registry['bash'])

        return PurdyLexer(*cls._registry['py3'])

    @classmethod
    def factory_from_name(cls, name):
        return PurdyLexer(*cls._registry[name])

    @classmethod
    def choices(cls):
        output = []
        for key, value in cls._registry.items():
            output.append(f'"{key}" ({value[1]})')

        return ', '.join([f'"{key}" ({value[1]})' for key, value in \
            cls._registry.items()])

    @classmethod
    def names(cls):
        return cls._registry.keys()

# -----------------------------------------------------------------------------

def token_is_a(token1, token2):
    """Returns true if token1 is the same type as or a child type of token2"""
    if token1 == token2:
        return True

    parent = token1.parent
    while(parent != None):
        if parent == token2:
            return True

        parent = parent.parent

    return False


def token_ancestor(token, ancestor_list):
    """Tokens are hierarchical, in some situations you need to translate a
    token into one from a known list, e.g. turning a
    "Token.Literal.Number.Integer" into a "Number". This method takes a token
    and a list of approved ancestors and attempts to make the map. If no
    ancestor is found then a generic "Token" object is returned

    :param token: token to translate into an approved ancestor
    :param ancestor_list: list of approved ancestor tokens
    """
    if token in ancestor_list:
        return token

    # token not in the approved list, search its ancestors
    token = token.parent
    while(token != None):
        if token in ancestor_list:
            return token

        token = token.parent

    # something went wrong with our lookup, return the default
    return Token

# ===========================================================================
# Purdy Code Representation 
# ===========================================================================

CodePart = namedtuple('CodePart', ['token', 'text'])


class BlankCodeLine:
    def render_line(self, colourizer):
        return ''


class FoldedCodeLine:
    def __init__(self, size):
        self.size = size

    def __eq__(self, other):
        if self.size == other.size:
            return True

        return False

    def render_line(self, colourizer):
        return colourizer.colourize(self)


class CodeLine:
    def __init__(self, parts, lexer, line_number=-1, highlight=False):
        """Represents a displayed line of code.

        :param parts: list of :code:`CodePart` objects that correspond to 
                       this line of code
        :param lexer: PurdyLexer used to parse the content
        :param line_number: line number for the line, -1 for off (default)
        :param highlight: True if this line is currently highlighted. Defaults
                          to False.
        """
        # too many bugs caused by a change to the parts list after the
        # CodeLine was created, copy the damn thing so it is internal only
        self.parts = deepcopy(parts)       
        self.lexer = lexer
        self.line_number = line_number
        self.highlight = highlight

        self.text = ''.join([part.text for part in parts])

    def __str__(self):
        num = ''
        if self.line_number > -1:
            num = f'{self.line_number:3} '
        return f'CodeLine("{num}{self.text}")'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # for testing purposes we want a comparison of content values, not of
        # the references
        if self.line_number != other.line_number or \
                self.highlight != other.highlight or \
                self.lexer.__class__ != other.lexer.__class__:
            return False

        for x, part, in enumerate(self.parts):
            if part.token != other.parts[x].token or \
                    part.text != other.parts[x].text:
                return False

        return True

    def render_line(self, colourizer):
        return colourizer.colourize(self)


def parse_source(source, lexer):
    """Parses blocks of source text, returning a list of :class:`CodeLine` 
    objects.
    """
    parser = _Parser(lexer)
    parser.parse(source)

    return parser.lines


class _Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.lines = []

    def parse(self, content):
        self.parts = []
        for token_type, text in self.lexer.pygments_lexer.get_tokens(content):
            if text.startswith('\n'):
                self.newline_handler(token_type)
                if len(text) > 1:
                    # something came after the \n, handle it
                    self.string_handler(token_type, text[1:])
            elif text == '':
                # tokenizer sometimes puts in empty stuff, skip it
                continue
            elif token_is_a(token_type, String) and '\n' in text:
                self.string_handler(token_type, text)
            else:
                self.default_handler(token_type, text)

    def newline_handler(self, token):
        # hit a CR, time to create a new CodeLine object
        if not self.parts:
            part = CodePart(token, '')
            self.parts = [part, ]

        self.lines.append( CodeLine(self.parts, self.lexer) )

        # reset to start the next set of tokens
        self.parts = []

    def string_handler(self, token, text):
        # String tokens may be multi-line
        for line in text.splitlines(True):
            part = CodePart(token, line.rstrip('\n'))
            self.parts.append(part)

            if line[-1] == '\n':
                self.lines.append( CodeLine(self.parts, self.lexer) )
                self.parts = []

    def default_handler(self, token, text):
        if text[-1] == '\n':
            # there is a \n at the end of the text, need to rebuild it
            # without it, then create the CodeLine object
            part = CodePart(token, text.rstrip('\n'))
            self.parts.append(part)

            # text caused a CR, create a new CodeLine object
            self.lines.append( CodeLine(self.parts, self.lexer ) )

            # reset to start the next group of tokens
            self.parts = []
        else:
            part = CodePart(token, text)
            self.parts.append(part)
