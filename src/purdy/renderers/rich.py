# renderers/rich.py
from pygments.token import Token, Whitespace

from purdy.parser import HighlightOn, HighlightOff
from purdy.renderers.formatter import Formatter, FormatHookBase

# ===========================================================================

class RichHook(FormatHookBase):
    def map_tag(self, tag_map, token, fg, bg, attrs, exceptions):
        if token in exceptions:
            tag_map[token] = exceptions[token]
            return

        # Default handling
        if not (fg or bg or attrs):
            # No formatting
            tag_map[token] = "%s"
            return

        tag_map[token] = f"[#{fg} {attrs}]%s[/]"


_CODE_TAG_EXCEPTIONS = {
    Token:              "%s",
    Whitespace:         "%s",

    # Purdy tokens
    HighlightOn:        "[reverse]%s",
    HighlightOff:       "[/reverse]",
}

# ===========================================================================

def to_rich(style):
    """Transforms tokenized content in a :class:`Code` object into a string
    with Rich library formatting.

    :param style: :class:`Style` object containing `Code` and `Theme` to
        translate
    """
    code = style.decorate()
    hook = RichHook()
    formatter = Formatter(style.theme, hook, _CODE_TAG_EXCEPTIONS)

    ancestor_list = style.theme.colour_map.keys()
    result = formatter.percent_s(code, ancestor_list)

    return result
