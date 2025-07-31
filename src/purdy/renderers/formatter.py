# renderers/formatter.py
from purdy.parser import token_ancestor

# =============================================================================

class Formatter:
    def __init__(self):
        self.tag_map = {}
        self.newline = "\n"
        self.escape = lambda x:x

    def create_tag_map(self, theme, exceptions):
        for token, fg, bg, attrs in theme.values():
            self._map_tag(token, fg, bg, attrs, exceptions)

    def format_doc(self, code, ancestor_list):
        result = ""
        for line in code:
            result += self.format_line(line, ancestor_list)

        return result

    def _map_tag(self, token, fg, bg, attrs, exceptions):
        raise NotImplementedError()

    def format_line(self, line, ancestor_list):
        raise NotImplementedError()


class StrFormatter(Formatter):
    ### Uses str.format() to create stylized output from code; assumes the
    # ._map_tag() method populated using {text} for any token text to be
    # inserted

    def format_line(self, line, ancestor_list):
        result = ""
        for part in line.parts:
            token = token_ancestor(part.token, ancestor_list)
            token_text = self.escape(part.text)

            try:
                marker = self.tag_map[token]
                result += marker.format(text=token_text)
            except KeyError:
                result += token_text

        if line.has_newline:
            result += self.newline

        return result
