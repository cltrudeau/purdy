# renderers/html.py
from html import escape as html_escape

from pygments.token import Token, Whitespace

from purdy.content import Code, Document, RenderState
from purdy.parser import HighlightOn, HighlightOff
from purdy.renderers.formatter import StrFormatter

# ===========================================================================

class HTMLFormatter(StrFormatter):
    def __init__(self, section, exceptions):
        super().__init__(section, exceptions)
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

    :param container: :class:`Code` or :class:`Document` object to translate
    :param snippet: When True [default] only show the code in a <div>,
        otherwise wrap it in full HTML document tags.
    """
    if isinstance(container, Code):
        container = Document(container)

    render_state = RenderState(container)

    # Header
    if not snippet:
        render_state.content += HTML_HEADER

    for section in container:
        if container.background is None:
            bg = "222222"
        else:
            bg = container.background

        render_state.content += (
            f'<div style="background :#{bg}; overflow:auto; width:auto; '
            'border:solid gray; border-width:.1em .1em .1em .8em; '
            'padding:.2em .6em;"><pre style="margin: 0; line-height:125%">'
        )

        render_state.formatter = HTMLFormatter(section, _CODE_TAG_EXCEPTIONS)
        section.render(render_state)

    if not snippet:
        render_state.content += HTML_FOOTER

    return render_state.content
