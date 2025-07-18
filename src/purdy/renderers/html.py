# renderers/html.py
from html import escape

from pygments.token import Token, Whitespace

from purdy.parser import HighlightOn, HighlightOff
from purdy.renderers.formatter import Formatter

# ===========================================================================

def _format_builder(tag_map, token, fg, bg, attrs, exceptions):
    if token in exceptions:
        tag_map[token] = exceptions[token]
        return

    # Default handling
    if not (fg or bg or attrs):
        # No formatting
        tag_map[token] = "%s"
        return

    tag = ""
    if fg or bg:
        tag = '<span style="'

        if fg:
            tag += f"color: #{fg}; "

        if bg:
            tag += f"background: #{bg}; "

        tag += '">'

    if "bold" in attrs:
        tag += "<b>"

    tag += "%s"

    if "bold" in attrs:
        tag += "</b>"

    if fg or bg:
        tag += '</span>'

    tag_map[token] = tag


_CODE_TAG_EXCEPTIONS = {
    Token:              '%s',
    Whitespace:         '%s',

    # Purdy tokens
    HighlightOn:        '<span style="background: white;">',
    HighlightOff:       '</span>',
}

# ===========================================================================

HTML_HEADER = """\
<!doctype html>
<html lang="en">
<body>
"""

HTML_FOOTER = """\
</body>
</html>
"""

def to_html(style, snippet=True):
    """Transforms tokenized content in a :class:`Code` object into a string
    representation of HTML.

    :param code: `Code` object to translate
    :param theme: Theme used for colourization
    :param snippet: When True [default] only show the code in a <div>,
        otherwise wrap it in full HTML document tags.
    """
    code = style.decorate()
    formatter = Formatter(style.theme, _format_builder, _CODE_TAG_EXCEPTIONS)

    ancestor_list = style.theme.colour_map.keys()

    result = ""

    # Header
    if not snippet:
        result += HTML_HEADER

    if style.background is None:
        bg = "222222"
    else:
        bg = style.background

    result += (
        f'<div style="background :#{bg}; overflow:auto; width:auto; '
        'border:solid gray; border-width:.1em .1em .1em .8em; '
        'padding:.2em .6em;"><pre style="margin: 0; line-height:125%">'
    )

    result += formatter.percent_s(code, ancestor_list, escape)

    if not snippet:
        result += HTML_FOOTER

    return result
