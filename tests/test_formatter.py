from unittest import TestCase

from pygments.token import Keyword, Name, Comment, Whitespace

from purdy.parser import Parser, CodePart
from purdy.renderers.formatter import Formatter, StrFormatter
from purdy.themes import Theme

from shared import code_liner

# =============================================================================

class DummyFormatter(StrFormatter):
    def _map_tag(self, token, fg, bg, attrs, exceptions):
        if token in exceptions:
            self.tag_map[token] = exceptions[token]
            return

        self.tag_map[token] = "text='{text}' " + \
            f"fg:'{fg}' bg:'{bg}' attrs:'{attrs}'"

DUMMY_FORMATTED = """\
not_ancestor
text='comment' fg:'112233' bg:'' attrs:''
text='keyword' fg:'223344' bg:'556677' attrs:'bold'
no_percent
"""

DUMMY_FORMATTED_ESCAPED = """\
<not_ancestor>
text='<comment>' fg:'112233' bg:'' attrs:''
text='<keyword>' fg:'223344' bg:'556677' attrs:'bold'
no_percent
"""

# =============================================================================

class TestFormatter(TestCase):
    def test_formatter(self):
        parser = Parser("py")

        theme = Theme({
            Comment: "112233",
            Keyword: ("223344", "556677", "bold"),
            Name: "667788",
        })
        ancestor_list = theme.colour_map.keys()

        # `Code` inherits from list, so just use a list in this case
        code = [
            code_liner(parser.spec, True, CodePart(Whitespace, 'not_ancestor')),
            code_liner(parser.spec, True, CodePart(Comment, 'comment')),
            code_liner(parser.spec, True, CodePart(Keyword, 'keyword')),
            code_liner(parser.spec, True, CodePart(Name, 'name')),
        ]

        exceptions = {
            Name: "no_percent",
        }

        # Default theme
        formatter = DummyFormatter()
        formatter.create_tag_map(theme, exceptions)
        result = formatter.format_doc(code, ancestor_list)
        self.assertEqual(DUMMY_FORMATTED, result)

        # Test with escape
        formatter.escape = lambda x: f"<{x}>"
        result = formatter.format_doc(code, ancestor_list)
        self.assertEqual(DUMMY_FORMATTED_ESCAPED, result)

        # Ensure abstractness
        base = Formatter()
        with self.assertRaises(NotImplementedError):
            base._map_tag(None, None, None, None, None)

        with self.assertRaises(NotImplementedError):
            base.format_line(None, None)
