# renderers/html.py
from html import escape as html_escape

from pygments.token import Token, Whitespace

from purdy.content import Code, MultiCode
from purdy.parser import HighlightOn, HighlightOff
from purdy.renderers.formatter import StrFormatter

# ===========================================================================

class HTMLFormatter(StrFormatter):
    def __init__(self):
        super().__init__()
        self.escape = html_escape

    def _map_tag(self, token, fg, bg, attrs, exceptions):
        if token in exceptions:
            self.tag_map[token] = exceptions[token]
            return

        # Default handling
        if not (fg or bg or attrs):
            # No formatting
            self.tag_map[token] = "{text}"
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

        tag += "{text}"

        if "bold" in attrs:
            tag += "</b>"

        if fg or bg:
            tag += '</span>'

        self.tag_map[token] = tag


_CODE_TAG_EXCEPTIONS = {
    Token:              '{text}',
    Whitespace:         '{text}',

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

def to_html(container, snippet=True):
    """Transforms tokenized content in a :class:`Code` object into a string
    representation of HTML.

    :param container: :class:`Code` or :class:`MultiCode` object to translate
    :param snippet: When True [default] only show the code in a <div>,
        otherwise wrap it in full HTML document tags.
    """
    result = ""
    if isinstance(container, Code):
        container = MultiCode(container)

    # Header
    if not snippet:
        result += HTML_HEADER

    for code_index in range(0, len(container)):
        formatter = HTMLFormatter()
        formatter.create_tag_map(container[code_index].theme,
            _CODE_TAG_EXCEPTIONS)

        if container.background is None:
            bg = "222222"
        else:
            bg = container.background

        result += (
            f'<div style="background :#{bg}; overflow:auto; width:auto; '
            'border:solid gray; border-width:.1em .1em .1em .8em; '
            'padding:.2em .6em;"><pre style="margin: 0; line-height:125%">'
        )

        result += formatter.format_doc(container, code_index)

    if not snippet:
        result += HTML_FOOTER

    return result
