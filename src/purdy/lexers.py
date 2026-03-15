"""
Lexers
======

Additional Lexers not included in Pygments

"""
import re

from pygments.lexer import Lexer
from pygments.lexers import BashSessionLexer
from pygments.token import Generic, Text

from purdy.tokens import TextualOutput, token_is_a

# =============================================================================

class DollarBashSessionLexer(BashSessionLexer):
    """Changes behaviour of the Pygments `BashSessionLexer` to assume a prompt
    uses a '$'. This allows better handling of virtual-env style prompts with
    lots of stuff left of the '$'.
    """
    _ps1rgx = re.compile(r'^([^$]*[$]\s)(.*\n?)')


class TUIDollarBashSessionLexer(DollarBashSessionLexer):
    """Based on custom DollarBashSessionLexer but does additional processing
    on output tokens to handle Textual TUI markup."""

    def get_tokens_unprocessed(self, text):
        # User parent's processor, just do further more work when it is an
        # Output token
        for item in super().get_tokens_unprocessed(text):
            if token_is_a(item[1], Generic.Output) and "[" in item[2]:
                yield (item[0], TextualOutput, item[2])
            else:
                yield item


class NewlineLexer(Lexer):
    """Treats each line in the body as a Pygments `Generic.Output` token"""
    name = "Newline output"
    aliases = ["newline"]

    def get_tokens_unprocessed(self, text):
        for token in text.split("\n"):
            yield 0, Generic.Output, token
            yield 0, Text, "\n"
