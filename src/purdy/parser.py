"""
Parser
=======

Contains methods and classes to manage parsing of code.
"""
from dataclasses import dataclass

from pygments.lexers import (PythonConsoleLexer, PythonLexer, BashSessionLexer,
    NodeConsoleLexer)
from pygments.lexers.data import YamlLexer
from pygments.lexers.markup import MarkdownLexer, RstLexer
from pygments.lexers.templates import HtmlDjangoLexer
from pygments.token import String, Token

from purdy.lexers import DollarBashSessionLexer, NewlineLexer

# =============================================================================
# Token Utilities
# =============================================================================

# Create new token types using Pygment's tuple magic
HighlightOn = Token.HighlightOn
HighlightOff = Token.HighlightOff
Fold = Token.Fold
LineNumber = Token.LineNumber


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


# =============================================================================
# Lexer Manager
# =============================================================================

@dataclass
class LexerSpec:
    name: str
    description: str
    lexer_cls: object
    console: bool
    style: str
    aliases: list = None


_built_in_specs = [
    LexerSpec('repl', 'Interactive Python 3 console', PythonConsoleLexer, True,
        'code'),
    LexerSpec('py', 'Python 3 Source', PythonLexer, False, 'code'),
    LexerSpec('con', 'Interactive bash console', BashSessionLexer, True,
        'code'),
    LexerSpec('dbash', 'Interactive bash Console with a dollar-sign prompt',
        DollarBashSessionLexer, True, 'code'),
    LexerSpec('node', 'Interactive JavaScript Node.js Console',
        NodeConsoleLexer, True, 'code'),
    LexerSpec('yaml', 'YAML Doc', YamlLexer, False, 'doc', ['yml']),
    LexerSpec('rst', 'RST Doc', RstLexer, False, 'doc'),
    LexerSpec('md', 'Markdown Doc', MarkdownLexer, False, 'doc'),
    LexerSpec('plain', 'Plain text, no parsing', NewlineLexer, False, 'doc',
        ['txt']),
    LexerSpec('html', 'HTML/Django/Jinja', HtmlDjangoLexer, False, 'xml',
        ['htm']),
]


@dataclass
class CodePart:
    token: Token
    text: str


@dataclass
class CodeLine:
    spec: LexerSpec
    parts: list

    def __repr__(self):
        return f"CodeLine(spec='{self.spec.name}', parts={self.parts})"

    def __eq__(self, compare):
        if self.spec.name != compare.spec.name:
            return False

        if len(self.parts) != len(compare.parts):
            return False

        for num, part in enumerate(self.parts):
            if part != compare.parts[num]:
                return False

        return True


class Parser:
    """This Parser is built on top of Pygments Lexers. A number of lexers are
    built-in to purdy but you can also create your own parser with any
    :class:`pygments.lexers.Lexer` class.
    """
    names = [spec.name for spec in _built_in_specs]

    def __init__(self, spec):
        self.spec = spec

    @classmethod
    def choices(cls):
        """Returns a string with the names and descriptions of each available
        lexer spec."""
        output = [f"'{spec.name}' ({spec.description})" for spec in \
            _built_in_specs]
        return ', '.join(output)

    @classmethod
    def custom(cls, name, description, pygments_lexer_cls, is_console, style):
        spec = LexerSpec(name, description, pygments_lexer_cls, is_console,
            style)

        return Parser(spec)

    @classmethod
    def from_name(cls, name):
        # Search through the spec's for a matching name or alias
        for spec in _built_in_specs:
            if name.lower() == spec.name:
                return Parser(spec)

            if spec.aliases is not None:
                for alias in spec.aliases:
                    if name.lower() == alias:
                        return Parser(spec)

        error = f"Unknown lexer *{name}*. Choices are: "
        error += cls.names.join(',')
        raise AttributeError(error)

    def parse(self, content):
        lexer = self.spec.lexer_cls()
        self.lines = []
        self.line = CodeLine(self.spec, [])
        for token_type, text in lexer.get_tokens(content):
            if text.startswith('\n'):
                self._newline_handler(token_type)
                if len(text) > 1:
                    # something came after the \n, handle it
                    self._string_handler(token_type, text[1:])
            elif text == '':
                # tokenizer sometimes puts in empty stuff, skip it
                continue
            elif token_is_a(token_type, String) and '\n' in text:
                self._string_handler(token_type, text)
            else:
                self._default_handler(token_type, text)

        # Pygments ensures strings are newline ended before passing them to
        # the lexer, our last line is likely going to be extra, double check
        # (in case the behaviour is inconsistent) and remove it
        if len(self.lines[-1].parts) == 1 and \
                self.lines[-1].parts[0].text == '':
            del self.lines[-1]

        return self.lines

    def _newline_handler(self, token_type):
        # hit a CR, time to create a new line
        if not self.line.parts:
            self.line = CodeLine(self.spec, [CodePart(token_type, '')])

        self.lines.append(self.line)

        # reset to start the next set of tokens
        self.line = CodeLine(self.spec, [])

    def _string_handler(self, token_type, text):
        # String tokens may be multi-line
        for row in text.splitlines(True):
            part = CodePart(token_type, row.rstrip('\n'))
            self.line.parts.append(part)

            if row[-1] == '\n':
                self.lines.append(self.line)
                self.line = CodeLine(self.spec, [])

    def _default_handler(self, token_type, text):
        if text[-1] == '\n':
            # there is a \n at the end of the text, need to rebuild it
            # without it, then create the line
            part = CodePart(token_type, text.rstrip('\n'))
            self.line.parts.append(part)

            # text caused a CR, create a new line object
            self.lines.append(self.line)

            # reset to start the next group of tokens
            self.line = CodeLine(self.spec, [])
        else:
            part = CodePart(token_type, text)
            self.line.parts.append(part)


# Dynamically add list of lexer choices to Parser's doc string
Parser.__doc__ += "\n".join([
    f"    * '{spec.name}' -- {spec.description}" for spec in _built_in_specs
])
