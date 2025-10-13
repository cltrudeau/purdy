from unittest import TestCase

from pygments.token import Comment, Keyword, Name, Whitespace

from purdy.content import Code, Document, RenderState
from purdy.parser import CodePart, Parser
from purdy.renderers.formatter import StrFormatter
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
        lexer_spec = parser.lexer_spec

        theme = Theme("dummy", {
            Comment: "112233",
            Keyword: ("223344", "556677", "bold"),
            Name: "667788",
        })

        # Hack up a Code object to use our theme and our hand crafted lines
        code = Code.text("", "plain")
        code.theme = theme
        code.lines = [
            code_liner(lexer_spec, True, CodePart(Whitespace, 'not_ancestor')),
            code_liner(lexer_spec, True, CodePart(Comment, 'comment')),
            code_liner(lexer_spec, True, CodePart(Keyword, 'keyword')),
            code_liner(lexer_spec, True, CodePart(Name, 'name')),
        ]
        doc = Document(code)
        section = doc[0]

        exceptions = {
            Name: "no_percent",
        }

        # Default theme
        rs = RenderState(doc)
        rs.formatter = DummyFormatter(section, exceptions)
        section.render(rs)
        self.assertEqual(DUMMY_FORMATTED, rs.content)

        # Test with escape
        rs = RenderState(doc)
        rs.formatter = DummyFormatter(section, exceptions)
        rs.formatter.escape = lambda x: f"<{x}>"
        section.render(rs)
        self.assertEqual(DUMMY_FORMATTED_ESCAPED, rs.content)
