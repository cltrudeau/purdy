from pathlib import Path
from unittest import TestCase

from pygments.token import Token

from purdy.parser import (CodeLine, CodePart, HighlightOn, HighlightOff,
    LexerSpec)
from purdy.content import Code, Stylizer
from purdy.renderers.plain import plain

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

class TestCode(TestCase):
    def test_code(self):
        text = "\n".join([str(x) for x in range(0, 10)]) + "\n"

        # Constructor as factory
        path = (Path(__file__).parent / Path("data/count.txt")).resolve()
        code = Code(path, "plain")

        self.assertEqual(10, len(code))
        self.assertEqual("0", code[0].parts[0].text)
        self.assertEqual("9", code[9].parts[0].text)

        # Text based factory
        code = Code.text(text, "plain")

        self.assertEqual(10, len(code))
        self.assertEqual("0", code[0].parts[0].text)
        self.assertEqual("9", code[9].parts[0].text)

        # Spawn
        spawn = code.spawn()
        self.assertEqual(code.parser, spawn.parser)
        self.assertEqual(0, len(spawn))


class TestStylizer(TestCase):
    def test_folding(self):
        # Sample text numbers 1-10 separated by newlines
        text = "\n".join([str(x) for x in range(0, 10)]) + "\n"
        style = Stylizer(Code.text(text, "plain"))

        # Fold lines 2 through 9
        style.fold(1, 8)
        output = style.apply(plain)
        expected = "0\n⠇\n9\n"
        self.assertEqual(expected, output)

        # Folding line[1], length=8 means that eight items of metadata get
        # created, validate that nothing else got created accidentally
        self.assertEqual(8, len(style.meta))

        # Unfold
        style.unfold(1)
        output = style.apply(plain)
        expected = "0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n"
        self.assertEqual(expected, output)
        self.assertEqual(8, len(style.meta))

        # Multiple folds
        style.fold(1, 1)
        style.fold(5, 2)
        output = style.apply(plain)

        expected = "0\n⠇\n2\n3\n4\n⠇\n7\n8\n9\n"
        self.assertEqual(expected, output)
        self.assertEqual(8, len(style.meta))

        # Unfold when multi-folded
        style.unfold(1)
        output = style.apply(plain)
        self.assertEqual(8, len(style.meta))

        expected = "0\n1\n2\n3\n4\n⠇\n7\n8\n9\n"
        self.assertEqual(expected, output)
        self.assertEqual(8, len(style.meta))

        # Error handling, double-fold
        with self.assertRaises(ValueError):
            style.fold(6, 1)

        # Make sure all this mucking about hasn't created unnecessary sparse
        # entries
        self.assertEqual(8, len(style.meta))

        # Error handling, unfold something not folded
        style.reset_metadata()
        with self.assertRaises(ValueError):
            style.unfold(0)

    def test_wrapping(self):
        path = (Path(__file__).parent / Path("data/wrap.py")).resolve()
        style = Stylizer(Code(path))

        # Default, no wrapping case
        expected = [style.code[0]]
        result = style.apply_wrapping(style.code[0])
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
        style.wrap = 35
        result = style.apply_wrapping(style.code[2])
        self.assertEqual(2, len(result))
        self.assertEqual("a long ", result[0].parts[-1].text)
        self.assertEqual("string", result[1].parts[0].text)

        # Wrap once midword at point 37
        style.wrap = 37
        result = style.apply_wrapping(style.code[2])
        self.assertEqual(2, len(result))
        self.assertEqual("a long ", result[0].parts[-1].text)
        self.assertEqual("string", result[1].parts[0].text)

        # Wrap twice at size 20
        style.wrap = 20
        result = style.apply_wrapping(style.code[2])
        self.assertEqual(4, len(result))
        self.assertEqual(" ", result[0].parts[-1].text)
        self.assertEqual("alpha", result[1].parts[0].text)
        self.assertEqual("a long ", result[1].parts[-1].text)
        self.assertEqual("string", result[2].parts[0].text)
        self.assertEqual("==", result[2].parts[-1].text)
        self.assertEqual(" ", result[3].parts[0].text)

        # Test full handling of plain.Code
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        style = Stylizer(Code(path))
        style.wrap = 35
        result = style.apply(plain)
        self.assertEqual(WRAPPED_SIMPLE, result)

    def test_line_numbers(self):
        text = "\n".join(["a" for x in range(0, 1001)]) + "\n"
        style = Stylizer(Code.text(text, "plain"))

        # Line numbers off
        self.assertEqual("", style.line_number(0))
        self.assertEqual("", style.line_number_gap())

        # Starting at 1 (default)
        style.line_numbers_enabled = True
        self.assertEqual("   1 ", style.line_number(0))
        self.assertEqual("1001 ", style.line_number(1000))

        # Starting at 10
        style.starting_line_number = 10
        self.assertEqual("  10 ", style.line_number(0))
        self.assertEqual("1010 ", style.line_number(1000))

        # Starting at 9_000
        style.starting_line_number = 9000
        self.assertEqual(" 9000 ", style.line_number(0))
        self.assertEqual("10000 ", style.line_number(1000))

        # Gap
        self.assertEqual("      ", style.line_number_gap())

        # Test full handling of renderers.plain
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        style = Stylizer(Code(path))
        style.line_numbers_enabled = True
        style.starting_line_number = 8

        result = style.apply(plain)
        self.assertEqual(NUMBERED_SIMPLE, result)

    def test_highlight_activation(self):
        text = "zero\none\ntwo\nthree and a bit\nfour and a bit"
        style = Stylizer(Code.text(text, "plain"))

        # Int index
        style.highlight(1)
        self.assertTrue(style.meta[1].highlight)
        style.reset_metadata()

        # Negative index
        style.highlight(-1)
        self.assertTrue(style.meta[4].highlight)
        style.reset_metadata()

        # Tuple (start, length)
        style.highlight( (1, 3) )
        self.assertTrue(style.meta[1].highlight)
        self.assertTrue(style.meta[2].highlight)
        self.assertTrue(style.meta[3].highlight)
        style.reset_metadata()

        # Tuple (negative, length)
        style.highlight( (-2, 2) )
        self.assertTrue(style.meta[3].highlight)
        self.assertTrue(style.meta[4].highlight)
        style.reset_metadata()

        # String range
        style.highlight("0-2")
        self.assertTrue(style.meta[0].highlight)
        self.assertTrue(style.meta[1].highlight)
        self.assertTrue(style.meta[2].highlight)
        style.reset_metadata()

        # Partial Highlighting
        style.highlight("3:6,3")
        self.assertEqual( [(6, 3)], style.meta[3].highlight_partial)
        style.reset_metadata()

        # Partial Highlighting, negative index
        style.highlight("-1:5,3")
        self.assertEqual( [(5, 3)], style.meta[4].highlight_partial)
        style.reset_metadata()

        # Mixed
        style.highlight(0, -1, "3:10,1")
        self.assertTrue(style.meta[0].highlight)
        self.assertTrue(style.meta[4].highlight)
        self.assertEqual( [(10, 1)], style.meta[3].highlight_partial)
        style.reset_metadata()

        # --- Test Highlight Off
        # Int
        style.highlight(1)
        style.highlight_off(1)
        self.assertEqual(1, len(style.meta))
        self.assertFalse(style.meta[1].highlight)
        style.reset_metadata()

        # Negative Int
        style.highlight(-1)
        style.highlight_off(-1)
        self.assertEqual(1, len(style.meta))
        self.assertFalse(style.meta[4].highlight)
        style.reset_metadata()

        # Tuple (start, length)
        style.highlight( (3, 2) )
        style.highlight_off( (3, 2) )
        self.assertEqual(2, len(style.meta))
        self.assertFalse(style.meta[3].highlight)
        self.assertFalse(style.meta[4].highlight)
        style.reset_metadata()

        # Tuple (negative start, length)
        style.highlight( (-1, 1) )
        style.highlight_off( (-1, 1) )
        self.assertEqual(1, len(style.meta))
        self.assertFalse(style.meta[4].highlight)
        style.reset_metadata()

        # String range, and goes past limit
        style.highlight("0-2")
        style.highlight_off("0-4")

        self.assertEqual(5, len(style.meta))
        for i in range(0, 5):
            self.assertFalse(style.meta[i].highlight)

        style.reset_metadata()

        # All off
        style.highlight("0-2")
        style.highlight_all_off()

        self.assertEqual(3, len(style.meta))
        for i in range(0, 3):
            self.assertFalse(style.meta[i].highlight)

        # Error handling: rejects partial
        with self.assertRaises(ValueError):
            style.highlight_off("0:1,4")

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
        result = Stylizer._chop_partial_highlight(line, [(4, 5)])
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

        result = Stylizer._chop_partial_highlight(line, [(3, 2)])
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

        result = Stylizer._chop_partial_highlight(line, [(7, 6)])
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

        result = Stylizer._chop_partial_highlight(line, [(3, 8)])
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

        result = Stylizer._chop_partial_highlight(line, [(3, 2), (7, 2)])
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
        style = Stylizer(Code.text(text, "plain"))

        # Test the token decoration process
        style.highlight(0, "3:0,5")
        result = style.apply_highlight(0)
        self.assertEqual(3, len(result.parts))
        self.assertEqual(Token.HighlightOn, result.parts[0].token)
        self.assertEqual("zero", result.parts[1].text)
        self.assertEqual(Token.HighlightOff, result.parts[2].token)

        result = style.apply_highlight(3)
        self.assertEqual(4, len(result.parts))
        self.assertEqual(Token.HighlightOn, result.parts[0].token)
        self.assertEqual("three", result.parts[1].text)
        self.assertEqual(Token.HighlightOff, result.parts[2].token)
        self.assertEqual(" and a bit", result.parts[3].text)

    def test_apply(self):
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        style = Stylizer(Code(path))
        style.wrap = 35
        style.line_numbers_enabled = True
        style.starting_line_number = 8
        style.fold(2, 3)

        result = style.apply(plain)
        self.assertEqual(WRAPPED_NUMBERED_SIMPLE, result)


## Dummy test to play with printing to the screen via rich
#class TestRich(TestCase):
#    def test_rich(self):
#        from purdy.renderers.rich_xfrm import rich_xfrm
#        from rich.console import Console
#
#        console = Console(highlight=False)
#
#        console.rule()
#
#        path = (Path(__file__).parent.parent /
#            Path("extras/display_code/code.py")).resolve()
#        style = Stylizer(Code(path))
#        style.wrap = 80
#        style.line_numbers_enabled = True
#        style.starting_line_number = 8
#        style.fold(2, 3)
#
#        result = style.apply(rich_xfrm)
#        console.print(result)
#
#        console.rule()
