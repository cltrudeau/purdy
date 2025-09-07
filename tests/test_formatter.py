from pathlib import Path
from unittest import TestCase

from pygments.token import Comment, Keyword, Name, Token, Whitespace

from purdy.content import Code, MultiCode
from purdy.parser import (CodeLine, CodePart, HighlightOn, HighlightOff,
    LexerSpec, Parser)
from purdy.renderers.formatter import Formatter, StrFormatter
from purdy.renderers.plain import to_plain
from purdy.themes import Theme

from shared import code_liner

# =============================================================================
# Result Constants
# =============================================================================

WRAPPED_SIMPLE = "\n".join([
    r'# Small file for simple parser ',
    r'testing',
    r'def simple(thing):',
    r'    """This tests',
    r'    multi-line strings"""',
    r'    return thing + "\nDone"',
    r'',
    r'simple("A string\nWith newline")',
    r'',
])

NUMBERED_SIMPLE = "\n".join([
    r' 8 # Small file for simple parser testing',
    r' 9 def simple(thing):',
    r'10     """This tests',
    r'11     multi-line strings"""',
    r'12     return thing + "\nDone"',
    r'13 ',
    r'14 simple("A string\nWith newline")',
    r'',
])

WRAPPED_NUMBERED_SIMPLE = "\n".join([
    r' 8 # Small file for simple parser ',
    r'testing',
    r' 9 def simple(thing):',
    r"10 ⠇",
    r'13 ',
    r'14 simple("A string\nWith newline")',
    r'',
])

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
        mc = MultiCode(code)

        exceptions = {
            Name: "no_percent",
        }

        # Default theme
        formatter = DummyFormatter()
        formatter.create_tag_map(theme, exceptions)
        result = formatter.format_doc(mc, 0)
        self.assertEqual(DUMMY_FORMATTED, result)

        # Test with escape
        formatter.escape = lambda x: f"<{x}>"
        result = formatter.format_doc(mc, 0)
        self.assertEqual(DUMMY_FORMATTED_ESCAPED, result)

        # Ensure abstractness
        base = Formatter()
        with self.assertRaises(NotImplementedError):
            base._map_tag(None, None, None, None, None)

        with self.assertRaises(NotImplementedError):
            base.format_line(None, None)

    def test_wrapping(self):
        path = (Path(__file__).parent / Path("data/wrap.py")).resolve()
        code = Code(path)
        mc = MultiCode(code)
        formatter = DummyFormatter()

        # Default, no wrapping case
        expected = [code.lines[0]]
        result = formatter._apply_wrapping(mc, code.lines[0])
        self.assertEqual(1, len(result))
        self.assertEqual(expected, result)

        # Test wrapping at different places.
        #
        # wrap.py line 3:
        #
        # if (alpha == 3 or alpha == "a long string") and beta == 5:
        #                    |              ^=35                |
        #                    ^=20              ^=split + 20     ^=split + 20

        # Wrap once on the space at point 35
        line = code.lines[2]
        mc.wrap = 35
        result = formatter._apply_wrapping(mc, line)
        self.assertEqual(2, len(result))
        self.assertEqual("a long ", result[0].parts[-1].text)
        self.assertEqual("string", result[1].parts[0].text)

        # Wrap once midword at point 37
        mc.wrap = 37
        result = formatter._apply_wrapping(mc, line)
        self.assertEqual(2, len(result))
        self.assertEqual("a long ", result[0].parts[-1].text)
        self.assertEqual("string", result[1].parts[0].text)

        # Wrap twice at size 20
        mc.wrap = 20
        result = formatter._apply_wrapping(mc, line)
        self.assertEqual(4, len(result))
        self.assertEqual(" ", result[0].parts[-1].text)
        self.assertEqual("alpha", result[1].parts[0].text)
        self.assertEqual("a long ", result[1].parts[-1].text)
        self.assertEqual("string", result[2].parts[0].text)
        self.assertEqual("==", result[2].parts[-1].text)
        self.assertEqual(" ", result[3].parts[0].text)

        # Test full handling of plain.Code
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        mc = MultiCode(Code(path))
        mc.wrap = 35
        result = to_plain(mc)
        self.assertEqual(WRAPPED_SIMPLE, result)

    def test_line_numbers(self):
        # Test full handling of renderers.plain
        #
        # The mechanics of line numbering is done in the MultiCode class, this
        # is just to check the full formatting works
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        mc = MultiCode(Code(path))
        mc.line_numbers_enabled = True
        mc.starting_line_number = 8

        result = to_plain(mc)
        self.assertEqual(NUMBERED_SIMPLE, result)

    def test_partial_highlight_chopping(self):
        ###
        # Tests the line chopping utility method for turning partial
        # highlights into tokenized line
        line = CodeLine(LexerSpec.built_ins["plain"])

        # Construct a line (|=token boundary, ^=Token.Keyword)
        # ZZZ|^|abcdefg|^|hijkl
        # 012|^|3456789|^|01234
        line.parts.extend([
            CodePart(Token.Text, "ZZZ"),
            CodePart(Token.Keyword, ""),     # handle empty token case
            CodePart(Token.Text, "abcdefg"),
            CodePart(Token.Keyword, ""),     # handle empty token case
            CodePart(Token.Text, "hijkl"),
        ])

        # !!! Note: the chop method uses (start, end) rather than the (start,
        # length) mechanism in the direct call to highlight()

        # Highlight within second grouping: chop (4, 5)
        #   x=highlighted part:
        #
        # ZZZ|^|abcdefg|^|hijkl
        #        xxxxx
        # 012   3456789   01234
        #
        # Expected: HL-On = {, HL-Off=}
        #    ZZZ|^|a|{|bcdef|}|g|^|hijkl

        # Chop is a classmethod, don't need an object
        result = Formatter._chop_partial_highlight(line, [(4, 5)])
        self.assertEqual(9, len(result.parts))
        self.assertEqual("a", result.parts[2].text)
        self.assertEqual(HighlightOn, result.parts[3].token)
        self.assertEqual("bcdef", result.parts[4].text)
        self.assertEqual(HighlightOff, result.parts[5].token)
        self.assertEqual("g", result.parts[6].text)

        # Highlight starting on a token boundary edge: (3, 2)
        #
        # ZZZ|^|abcdefg|^|hijkl
        #       xx
        # 012   3456789   01234
        #
        # Expected: HL-On = {, HL-Off=}
        #    ZZZ|^|{|ab|}|cdefg|^|hijkl

        result = Formatter._chop_partial_highlight(line, [(3, 2)])
        self.assertEqual(8, len(result.parts))
        self.assertEqual(HighlightOn, result.parts[2].token)
        self.assertEqual("ab", result.parts[3].text)
        self.assertEqual(HighlightOff, result.parts[4].token)
        self.assertEqual("cdefg", result.parts[5].text)
        self.assertEqual("hijkl", result.parts[7].text)

        # Highlight across boundaries: (7, 6)
        #
        # ZZZ|^|abcdefg|^|hijkl
        #           xxx   xxx
        # 012   3456789   01234
        #
        # Expected: HL-On = {, HL-Off=}
        #    ZZZ|^|abcd|{|efg|^|hij|}|kl

        result = Formatter._chop_partial_highlight(line, [(7, 6)])
        self.assertEqual(9, len(result.parts))
        self.assertEqual("abcd", result.parts[2].text)
        self.assertEqual(HighlightOn, result.parts[3].token)
        self.assertEqual("efg", result.parts[4].text)
        self.assertEqual(Token.Keyword, result.parts[5].token)
        self.assertEqual("hij", result.parts[6].text)
        self.assertEqual(HighlightOff, result.parts[7].token)
        self.assertEqual("kl", result.parts[8].text)

        # Highlight across full token and boundaries: (3, 8)
        #
        # ZZZ|^|abcdefg|^|hijkl
        #       xxxxxxx   x
        # 012   3456789   01234
        #
        # Expected: HL-On = {, HL-Off=}
        #    ZZZ|^|{|abcdefg|^|h|}|ijkl

        result = Formatter._chop_partial_highlight(line, [(3, 8)])
        self.assertEqual(8, len(result.parts))
        self.assertEqual(HighlightOn, result.parts[2].token)
        self.assertEqual("abcdefg", result.parts[3].text)
        self.assertEqual(Token.Keyword, result.parts[4].token)
        self.assertEqual("h", result.parts[5].text)
        self.assertEqual(HighlightOff, result.parts[6].token)
        self.assertEqual("ijkl", result.parts[7].text)

        # Highlight twice in the same line (3, 2) & (7, 2)
        #
        # ZZZ|^|abcdefg|^|hijkl
        #       xx  xx
        # 012   3456789   01234
        #
        # Expected: HL-On = {, HL-Off=}
        #    ZZZ|^|{|ab|}|cd|{|ef|}|g|^|hijkl

        result = Formatter._chop_partial_highlight(line, [(3, 2), (7, 2)])
        self.assertEqual(12, len(result.parts))
        self.assertEqual(HighlightOn, result.parts[2].token)
        self.assertEqual("ab", result.parts[3].text)
        self.assertEqual(HighlightOff, result.parts[4].token)
        self.assertEqual("cd", result.parts[5].text)
        self.assertEqual(HighlightOn, result.parts[6].token)
        self.assertEqual("ef", result.parts[7].text)
        self.assertEqual(HighlightOff, result.parts[8].token)
        self.assertEqual("g", result.parts[9].text)
        self.assertEqual(Token.Keyword, result.parts[10].token)
        self.assertEqual("hijkl", result.parts[11].text)

    def test_highlight_applied(self):
        text = "zero\none\ntwo\nthree and a bit\nfour and a bit"
        code = Code.text(text, "plain")
        formatter = DummyFormatter()

        # Test that highlight tokens get inserted properly
        code.highlight(0, "3:0,5")

        # Highlighted all of line 0
        result = formatter._apply_highlight(code, 0)
        self.assertEqual(3, len(result.parts))
        self.assertEqual(Token.HighlightOn, result.parts[0].token)
        self.assertEqual("zero", result.parts[1].text)
        self.assertEqual(Token.HighlightOff, result.parts[2].token)

        # Highlighted line 3 characters 0-4
        result = formatter._apply_highlight(code, 3)
        self.assertEqual(4, len(result.parts))
        self.assertEqual(Token.HighlightOn, result.parts[0].token)
        self.assertEqual("three", result.parts[1].text)
        self.assertEqual(Token.HighlightOff, result.parts[2].token)
        self.assertEqual(" and a bit", result.parts[3].text)

    def test_get_decorated_lines(self):
        # The to_plain() method invokes get_decorated_lines underneath, this
        # method applies a lot of motif options to make sure everything gets
        # tickled
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        mc = MultiCode(Code(path))
        mc.wrap = 35
        mc.line_numbers_enabled = True
        mc.starting_line_number = 8
        mc[0].fold(2, 3)

        result = to_plain(mc)
        self.assertEqual(WRAPPED_NUMBERED_SIMPLE, result)
