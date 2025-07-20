# renderers/formatter.py
from purdy.parser import token_ancestor

# =============================================================================

class FormatHookBase:
    def __init__(self):
        self.newline = "\n"
        self.escape = lambda x:x

    def map_tag(self, tag_map, token, fg, bg, attrs, exceptions):
        raise NotImplementedError()

# -----------------------------------------------------------------------------

class Formatter:
    def __init__(self, theme, hook, exceptions=None):
        self.tag_map = {}
        self.hook = hook
        for token, fg, bg, attrs in theme.values():
            hook.map_tag(self.tag_map, token, fg, bg, attrs, exceptions)

    def percent_s_line(self, line, ancestor_list):
        result = ""
        for part in line.parts:
            token = token_ancestor(part.token, ancestor_list)
            try:
                marker = self.tag_map[token]
                if "%s" in marker:
                    result += marker % self.hook.escape(part.text)
                else:
                    result += marker
            except KeyError:
                result += self.hook.escape(part.text)

        if line.has_newline:
            result += self.hook.newline

        return result

    def percent_s(self, code, ancestor_list):
        result = ""
        for line in code:
            result += self.percent_s_line(line, ancestor_list)

        return result
