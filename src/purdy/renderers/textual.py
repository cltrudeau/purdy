# renderers/textual.py
from pygments.token import Token, Whitespace
from textual.content import Content

from purdy.parser import HighlightOn, HighlightOff, token_ancestor
from purdy.renderers.formatter import conversion_handler, Formatter

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
        # Textual really doesn't like piecemeal creation of content or
        # strings, and they way the code works elsewhere you can just append a
        # close attr, but here you can't
        #
        # You need to construct a single string for the Content.from_markup
        # method, which means having to be a bit hacky, creating then
        # re-parsing the individual pieces

        part_map = {}
        counter = 0
        markup = ""

        for part in line.parts:
            token = token_ancestor(part.token, ancestor_list)

            name = f"text_{counter}"
            dname = "$" + name

            try:
                # Get the tag from the general map and replace $text with the
                # counted version
                marker = self.tag_map[token]
                marker = marker.replace("$text", dname)
            except KeyError:
                # No map tags, use just the placeholder for the content
                marker = dname

            # Store the text for Content's kwargs and update our markup
            # string
            part_map[name] = part.text
            markup += marker

            counter += 1

        if line.has_newline:
            markup += self.newline

        # Now get Textual to render that mess
        return Content.from_markup(markup, **part_map)


_CODE_TAG_EXCEPTIONS = {
    Token:              "$text",
    Whitespace:         "$text",

    # Purdy tokens
    HighlightOn:        "[reverse]$text",
    HighlightOff:       "[/reverse]",
}

# ===========================================================================

def to_textual(container):
    """Transforms tokenized content in a :class:`Code` object into a string
    with Textual library formatting.

    :param container: :class:`Code` or :class:`MultiCode` object to translate
    """
    return conversion_handler(TextualFormatter, container,
        _CODE_TAG_EXCEPTIONS)
