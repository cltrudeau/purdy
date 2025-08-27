from pathlib import Path
from unittest import TestCase

from pygments.token import Token

from purdy.parser import (CodeLine, CodePart, HighlightOn, HighlightOff,
    LexerSpec)
from purdy.content import Code
from purdy.themes import Theme
from purdy.motif import Motif
from purdy.renderers.plain import to_plain

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

class TestMotif(TestCase):
    def test_motif_init(self):
        # The rest of the tests hit most of the Motif class, this just tickles
        # the bits that don't get run
        theme = Theme({})
        motif = Motif(Code.text("", "plain"), theme)
        self.assertEqual(theme, motif.theme)


    def test_folding(self):
        # Sample text numbers 1-10 separated by newlines
        text = "\n".join([str(x) for x in range(0, 10)]) + "\n"
        motif = Motif(Code.text(text, "plain"))

        # Fold lines 2 through 9
        motif.fold(1, 8)
        output = to_plain(motif)
        expected = "0\n⠇\n9\n"
        self.assertEqual(expected, output)

        # Folding line[1], length=8 means that eight items of metadata get
        # created, validate that nothing else got created accidentally
        self.assertEqual(8, len(motif.meta))

        # Unfold
        motif.unfold(1)
        output = to_plain(motif)
        expected = "0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n"
        self.assertEqual(expected, output)
        self.assertEqual(8, len(motif.meta))

        # Multiple folds
        motif.fold(1, 1)
        motif.fold(5, 2)
        output = to_plain(motif)

        expected = "0\n⠇\n2\n3\n4\n⠇\n7\n8\n9\n"
        self.assertEqual(expected, output)
        self.assertEqual(8, len(motif.meta))

        # Unfold when multi-folded
        motif.unfold(1)
        output = to_plain(motif)
        self.assertEqual(8, len(motif.meta))

        expected = "0\n1\n2\n3\n4\n⠇\n7\n8\n9\n"
        self.assertEqual(expected, output)
        self.assertEqual(8, len(motif.meta))

        # Error handling, double-fold
        with self.assertRaises(ValueError):
            motif.fold(6, 1)

        # Make sure all this mucking about hasn't created unnecessary sparse
        # entries
        self.assertEqual(8, len(motif.meta))

        # Error handling, unfold something not folded
        motif.reset_metadata()
        with self.assertRaises(ValueError):
            motif.unfold(0)

    def test_wrapping(self):
        path = (Path(__file__).parent / Path("data/wrap.py")).resolve()
        motif = Motif(Code(path))

        # Default, no wrapping case
        expected = [motif.code[0]]
        result = motif.apply_wrapping(motif.code[0])
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
        motif.wrap = 35
        result = motif.apply_wrapping(motif.code[2])
        self.assertEqual(2, len(result))
        self.assertEqual("a long ", result[0].parts[-1].text)
        self.assertEqual("string", result[1].parts[0].text)

        # Wrap once midword at point 37
        motif.wrap = 37
        result = motif.apply_wrapping(motif.code[2])
        self.assertEqual(2, len(result))
        self.assertEqual("a long ", result[0].parts[-1].text)
        self.assertEqual("string", result[1].parts[0].text)

        # Wrap twice at size 20
        motif.wrap = 20
        result = motif.apply_wrapping(motif.code[2])
        self.assertEqual(4, len(result))
        self.assertEqual(" ", result[0].parts[-1].text)
        self.assertEqual("alpha", result[1].parts[0].text)
        self.assertEqual("a long ", result[1].parts[-1].text)
        self.assertEqual("string", result[2].parts[0].text)
        self.assertEqual("==", result[2].parts[-1].text)
        self.assertEqual(" ", result[3].parts[0].text)

        # Test full handling of plain.Code
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        motif = Motif(Code(path))
        motif.wrap = 35
        result = to_plain(motif)
        self.assertEqual(WRAPPED_SIMPLE, result)

    def test_line_numbers(self):
        text = "\n".join(["a" for x in range(0, 1001)]) + "\n"
        motif = Motif(Code.text(text, "plain"))

        # Line numbers off
        self.assertEqual("", motif.line_number(0))
        self.assertEqual("", motif.line_number_gap())

        # Starting at 1 (default)
        motif.line_numbers_enabled = True
        self.assertEqual("   1 ", motif.line_number(0))
        self.assertEqual("1001 ", motif.line_number(1000))

        # Starting at 10
        motif.starting_line_number = 10
        self.assertEqual("  10 ", motif.line_number(0))
        self.assertEqual("1010 ", motif.line_number(1000))

        # Starting at 9_000
        motif.starting_line_number = 9000
        self.assertEqual(" 9000 ", motif.line_number(0))
        self.assertEqual("10000 ", motif.line_number(1000))

        # Gap
        self.assertEqual("      ", motif.line_number_gap())

        # Test full handling of renderers.plain
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        motif = Motif(Code(path))
        motif.line_numbers_enabled = True
        motif.starting_line_number = 8

        result = to_plain(motif)
        self.assertEqual(NUMBERED_SIMPLE, result)

    def test_highlight_activation(self):
        text = "zero\none\ntwo\nthree and a bit\nfour and a bit"
        motif = Motif(Code.text(text, "plain"))

        # Int index
        motif.highlight(1)
        self.assertTrue(motif.meta[1].highlight)
        motif.reset_metadata()

        # Negative index
        motif.highlight(-1)
        self.assertTrue(motif.meta[4].highlight)
        motif.reset_metadata()

        # Tuple (start, length)
        motif.highlight( (1, 3) )
        self.assertTrue(motif.meta[1].highlight)
        self.assertTrue(motif.meta[2].highlight)
        self.assertTrue(motif.meta[3].highlight)
        motif.reset_metadata()

        # Tuple (negative, length)
        motif.highlight( (-2, 2) )
        self.assertTrue(motif.meta[3].highlight)
        self.assertTrue(motif.meta[4].highlight)
        motif.reset_metadata()

        # String int
        motif.highlight("0")
        self.assertTrue(motif.meta[0].highlight)
        motif.reset_metadata()

        # String int negative
        motif.highlight("-1")
        self.assertTrue(motif.meta[4].highlight)
        motif.reset_metadata()

        # String range
        motif.highlight("0-2")
        self.assertTrue(motif.meta[0].highlight)
        self.assertTrue(motif.meta[1].highlight)
        self.assertTrue(motif.meta[2].highlight)
        motif.reset_metadata()

        # Partial Highlighting
        motif.highlight("3:6,3")
        self.assertEqual( [(6, 3)], motif.meta[3].highlight_partial)
        motif.reset_metadata()

        # Partial Highlighting, negative index
        motif.highlight("-1:5,3")
        self.assertEqual( [(5, 3)], motif.meta[4].highlight_partial)
        motif.reset_metadata()

        # Mixed
        motif.highlight(0, -1, "3:10,1")
        self.assertTrue(motif.meta[0].highlight)
        self.assertTrue(motif.meta[4].highlight)
        self.assertEqual( [(10, 1)], motif.meta[3].highlight_partial)
        motif.reset_metadata()

        # --- Test Highlight Off
        # Int
        motif.highlight(1)
        motif.highlight_off(1)
        self.assertEqual(1, len(motif.meta))
        self.assertFalse(motif.meta[1].highlight)
        motif.reset_metadata()

        # Negative Int
        motif.highlight(-1)
        motif.highlight_off(-1)
        self.assertEqual(1, len(motif.meta))
        self.assertFalse(motif.meta[4].highlight)
        motif.reset_metadata()

        # Tuple (start, length)
        motif.highlight( (3, 2) )
        motif.highlight_off( (3, 2) )
        self.assertEqual(2, len(motif.meta))
        self.assertFalse(motif.meta[3].highlight)
        self.assertFalse(motif.meta[4].highlight)
        motif.reset_metadata()

        # Tuple (negative start, length)
        motif.highlight( (-1, 1) )
        motif.highlight_off( (-1, 1) )
        self.assertEqual(1, len(motif.meta))
        self.assertFalse(motif.meta[4].highlight)
        motif.reset_metadata()

        # String range, and goes past limit
        motif.highlight("0-2")
        motif.highlight_off("0-4")

        self.assertEqual(5, len(motif.meta))
        for i in range(0, 5):
            self.assertFalse(motif.meta[i].highlight)

        motif.reset_metadata()

        # All off
        motif.highlight("0-2")
        motif.highlight_all_off()

        self.assertEqual(3, len(motif.meta))
        for i in range(0, 3):
            self.assertFalse(motif.meta[i].highlight)

        # Error handling: rejects partial
        with self.assertRaises(ValueError):
            motif.highlight_off("0:1,4")

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
        result = Motif._chop_partial_highlight(line, [(4, 5)])
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

        result = Motif._chop_partial_highlight(line, [(3, 2)])
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

        result = Motif._chop_partial_highlight(line, [(7, 6)])
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

        result = Motif._chop_partial_highlight(line, [(3, 8)])
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

        result = Motif._chop_partial_highlight(line, [(3, 2), (7, 2)])
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
        motif = Motif(Code.text(text, "plain"))

        # Test the token decoration process
        motif.highlight(0, "3:0,5")
        result = motif.apply_highlight(0)
        self.assertEqual(3, len(result.parts))
        self.assertEqual(Token.HighlightOn, result.parts[0].token)
        self.assertEqual("zero", result.parts[1].text)
        self.assertEqual(Token.HighlightOff, result.parts[2].token)

        result = motif.apply_highlight(3)
        self.assertEqual(4, len(result.parts))
        self.assertEqual(Token.HighlightOn, result.parts[0].token)
        self.assertEqual("three", result.parts[1].text)
        self.assertEqual(Token.HighlightOff, result.parts[2].token)
        self.assertEqual(" and a bit", result.parts[3].text)

    def test_decorate(self):
        # The to_plain() method invokes decorate underneath, this method
        # applies a lot of motif options to make sure everything gets tickled
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        motif = Motif(Code(path))
        motif.wrap = 35
        motif.line_numbers_enabled = True
        motif.starting_line_number = 8
        motif.fold(2, 3)

        result = to_plain(motif)
        self.assertEqual(WRAPPED_NUMBERED_SIMPLE, result)
