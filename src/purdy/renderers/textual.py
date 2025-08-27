# renderers/textual.py
from pygments.token import Token, Whitespace
from textual.content import Content

from purdy.parser import HighlightOn, HighlightOff, token_ancestor
from purdy.renderers.formatter import Formatter

# ===========================================================================

class TextualFormatter(Formatter):
    def _map_tag(self, token, fg, bg, attrs, exceptions):
        if token in exceptions:
            self.tag_map[token] = exceptions[token]
            return

        # Default handling
        if not (fg or bg or attrs):
            # No formatting
            self.tag_map[token] = "$text"
            return

        # Use f-string to inject rich markup, but raw string to insert the
        # brace brackets expected by .format_doc()
        self.tag_map[token] = f"[#{fg} {attrs}]$text[/]"

    def format_line(self, line, ancestor_list):
        result = ""
        for part in line.parts:
            token = token_ancestor(part.token, ancestor_list)

            try:
                marker = self.tag_map[token]
                result += Content.from_markup(marker, text=part.text)
            except KeyError:
                result += token_text

        if line.has_newline:
            result += self.newline

        return result


_CODE_TAG_EXCEPTIONS = {
    Token:              "$text",
    Whitespace:         "$text",

    # Purdy tokens
    HighlightOn:        "[reverse]$text",
    HighlightOff:       "[/reverse]",
}

# ===========================================================================

def to_textual(motif):
    """Transforms tokenized content in a :class:`Code` object into a string
    with Textual library formatting.

    :param motif: :class:`Motif` object containing `Code` and `Theme` to
        translate
    """
    code = motif.decorate()
    formatter = TextualFormatter()
    formatter.create_tag_map(motif.theme, _CODE_TAG_EXCEPTIONS)

    ancestor_list = motif.theme.colour_map.keys()
    result = formatter.format_doc(code, ancestor_list)

    return result
