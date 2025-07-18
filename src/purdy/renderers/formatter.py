# renderers/formatter.py
from purdy.parser import token_ancestor

# =============================================================================

class Formatter:
    def __init__(self, theme, builder_fn, exceptions=None):
        self.tag_map = {}
        for token, fg, bg, attrs in theme.values():
            builder_fn(self.tag_map, token, fg, bg, attrs, exceptions)

    def percent_s(self, code, ancestor_list):
        result = ""
        for line in code:
            for part in line.parts:
                token = token_ancestor(part.token, ancestor_list)
                try:
                    marker = self.tag_map[token]
                    if "%s" in marker:
                        result += marker % part.text
                    else:
                        result += marker
                except KeyError:
                    result += part.text

            if line.has_newline:
                result += "\n"

        return result
