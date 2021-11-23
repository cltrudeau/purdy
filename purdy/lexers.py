"""
Lexers
======

Additional Lexers not included in Pygments

"""
import re

from pygments.lexers import BashSessionLexer

# =============================================================================

class DollarBashSessionLexer(BashSessionLexer):
    """Changes behaviour of the BashSessionLexer to assume a prompt uses a
    '$'. This allows better handling of virtual-env style prompts with lots
    of stuff left of the '$'.
    """
    _ps1rgx = re.compile(r'^([^$]*[$]\s)(.*\n?)')
