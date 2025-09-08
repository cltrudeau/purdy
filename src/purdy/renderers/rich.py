# renderers/rich.py
from pygments.token import Token, Whitespace

from rich.markup import escape as rich_escape

from purdy.parser import HighlightOn, HighlightOff
from purdy.renderers.formatter import StrFormatter, conversion_handler

# ===========================================================================

class RichFormatter(StrFormatter):
    def __init__(self):
        super().__init__()
        self.escape = rich_escape

    def _map_tag(self, token, fg, bg, attrs, exceptions):
        if token in exceptions:
            self.tag_map[token] = exceptions[token]
            return

        # Default handling
        if not (fg or bg or attrs):
            # No formatting
            self.tag_map[token] = "{text}"
            return

        # Use f-string to inject rich markup, but raw string to insert the
        # brace brackets expected by .format_doc()
        self.tag_map[token] = f"[#{fg} {attrs}]" + r"{text}" + "[/]"


_CODE_TAG_EXCEPTIONS = {
    Token:              "{text}",
    Whitespace:         "{text}",

    # Purdy tokens
    HighlightOn:        "[reverse]{text}",
    HighlightOff:       "[/reverse]",
}

# ===========================================================================

def to_rich(container):
    """Transforms tokenized content in a :class:`Code` object into a string
    with Rich library formatting.

    :param container: `Code` or :class:`MultiCode` object to render
    """
    return conversion_handler(RichFormatter, container, _CODE_TAG_EXCEPTIONS)
