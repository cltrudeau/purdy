"""
Lexers
======

Additional Lexers not included in Pygments

"""
import re

from pygments.lexer import Lexer
from pygments.lexers import BashSessionLexer
from pygments.token import Generic, Text

# =============================================================================

class DollarBashSessionLexer(BashSessionLexer):
    """Changes behaviour of the BashSessionLexer to assume a prompt uses a
    '$'. This allows better handling of virtual-env style prompts with lots
    of stuff left of the '$'.
    """
    _ps1rgx = re.compile(r'^([^$]*[$]\s)(.*\n?)')


class NewlineLexer(Lexer):
    """Treats each line in the body as a Generic.Output token"""
    name = "Newline output"
    aliases = ["newline"]

    def get_tokens_unprocessed(self, text):
        for token in text.split("\n"):
            yield 0, Generic.Output, token
            yield 0, Text, "\n"
