"""
Parser
=======

Contains methods and classes to manage parsing of code.
"""
from dataclasses import dataclass, field
from pathlib import Path

from pygments.lexer import Lexer as Pygments_Lexer
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
    """LexerSpec wraps a Pygments Lexer and contains data that changes the
    behaviour of the display of the code.

    :param description: description text about what this LexerSpec is for
    :param lexer_cls: The Pygments Lexer class used for parsing
    :param console: True if the content is a REPL or console, False otherwise.
        This setting effects how animations and certain kinds of output are
        displayed
    :param style: Style classification to use for the colourization and
        rendering map
    """
    description: str
    lexer_cls: object
    console: bool
    style: str

    @classmethod
    def find(cls, name):
        name = name.lower()
        if name in cls.aliases:
            return cls.built_ins[cls.aliases[name]]

        try:
            return cls.built_ins[name]
        except KeyError:
            raise ValueError("Invalid LexerSpec name. Choices are:" +
                ",".join(cls.names))


LexerSpec.built_ins = {
    'repl': LexerSpec('Interactive Python 3 console', PythonConsoleLexer,
        True, 'code'),
    'py': LexerSpec('Python 3 Source', PythonLexer, False, 'code'),
    'con': LexerSpec('Interactive bash console', BashSessionLexer, True,
        'code'),
    'dbash': LexerSpec('Interactive bash Console with a dollar-sign prompt',
        DollarBashSessionLexer, True, 'code'),
    'node': LexerSpec('Interactive JavaScript Node.js Console',
        NodeConsoleLexer, True, 'code'),
    'yaml': LexerSpec('YAML Doc', YamlLexer, False, 'doc'),
    'rst': LexerSpec('RST Doc', RstLexer, False, 'doc'),
    'md': LexerSpec('Markdown Doc', MarkdownLexer, False, 'doc'),
    'plain': LexerSpec('Plain text, no parsing', NewlineLexer, False, 'doc'),
    'html': LexerSpec('HTML/Django/Jinja', HtmlDjangoLexer, False, 'xml'),
}

LexerSpec.aliases = {
    "htm": "html",
    "txt": "plain",
    "yml": "yaml",
}

LexerSpec.names = list(LexerSpec.built_ins.keys()) + \
    list(LexerSpec.aliases.keys())

# ---------------------------------------------------------------------------

@dataclass
class CodePart:
    token: Token
    text: str


@dataclass
class CodeLine:
    spec: LexerSpec
    parts: list = field(default_factory=list)
    has_newline: bool = False

    def __repr__(self):
        return (f"CodeLine({self.spec.lexer_cls.__name__=}, {self.parts=}, "
            f"{self.has_newline=})")

    def __eq__(self, compare):
        if self.spec.lexer_cls != compare.spec.lexer_cls:
            return False

        if len(self.parts) != len(compare.parts):
            return False

        for num, part in enumerate(self.parts):
            if part != compare.parts[num]:
                return False

        return True


class Parser:
    """Parser is responsible for parsing code and turning it into a series of
    :class:`CodeLine` objects. You configure a Parser with a
    :class:`LexerSpec` which wraps a Pygments Lexer. Several are built-in for
    ease of use, but you can also pass in any
    :class:`pygments.lexers.Lexer` class.
    """

    def __init__(self, identifier, hint=''):
        """Create a Parser object

        :param identifier: An indicator as to what underlying lexer to use. It
            can be the string "detect" to attempt to auto-detect the
            appropriate lexer, a string corresponding to one of the built-in
            :class:`LexerSpec` objects, a :class:`LexerSpec` itself, or a
            Pygments :class:`pygments.lexers.Lexer` class. When a Pygments
            Lexer is provided it is assumed to be for code and not in console
            mode.

        :param hint: when using identifier="detect", this provides information
            for doing the detection
        """
        match identifier:
            case "detect":
                # Assume the hint is a file name
                path = Path(hint)
                self.spec = LexerSpec.find(path.suffix[1:])
            case str(name):
                self.spec = LexerSpec.find(name)
            case LexerSpec():
                self.spec = identifier
            case _:
                if not issubclass(identifier, Pygments_Lexer):
                    raise ValueError("Could not determine Parser type")

                name = 'custom_' + identifier.__name__
                self.spec = LexerSpec(name, identifier, False, 'code')

    def parse(self, content):
        # Instantiate the lexer so that it doesn't remove starting newlines,
        # just keeps it the way the content is.
        #
        # NB: it would be nice to also use "ensurenl=False" to stop the stupid
        # appending newlines, but that breaks a whole bunch of the lexers
        lexer = self.spec.lexer_cls(stripnl=False)
        self.lines = []
        self.line = CodeLine(self.spec)
        for token_type, text in lexer.get_tokens(content):
            if text.startswith('\n'):
                self._newline_handler(token_type)
                if len(text) > 1:
                    # something came after the \n, handle it
                    #
                    # Example: HTML lexer isn't line oriented, so a \n
                    # followed by in indent is seeing as one chunk of text
                    self._string_handler(token_type, text[1:])
            elif text == '':
                # tokenizer sometimes puts in empty stuff, skip it
                #
                # Example: Python Console Lexer and Traceback output
                continue
            elif token_is_a(token_type, String) and '\n' in text:
                self._string_handler(token_type, text)
            else:
                self._default_handler(token_type, text)

        # Pygments adds newlines because some of the lexers need it there,
        # get rid of it
        last_line = self.lines[-1]
        if len(last_line.parts) == 1 and last_line.parts[0].text == '':
            # Got a garbage extra line, remove it
            del self.lines[-1]

        # Fix the last lines newline state
        self.lines[-1].has_newline = content[-1] == "\n"

        return self.lines

    def _newline_handler(self, token_type):
        # hit a CR, time to create a new line
        if not self.line.parts:
            self.line = CodeLine(self.spec, [CodePart(token_type, '')])

        self.line.has_newline = True
        self.lines.append(self.line)

        # reset to start the next set of tokens
        self.line = CodeLine(self.spec)

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
            # there is a \n at the end of the text, need to strip it out then
            # start a newline using the same token
            #
            # Example: this happens with multi-line output of a bash console
            # session
            part = CodePart(token_type, text.rstrip('\n'))
            self.line.parts.append(part)

            # text caused a CR, create a new line object
            self.line.has_newline = True
            self.lines.append(self.line)

            # reset to start the next group of tokens
            self.line = CodeLine(self.spec)
        else:
            part = CodePart(token_type, text)
            self.line.parts.append(part)
