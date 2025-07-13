from pathlib import Path
from unittest import TestCase

from purdy.content.plain import TextCode, Code

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

# =============================================================================

class TestCodeHandlers(TestCase):
    def test_access(self):
        # Sample text numbers 1-10 separated by newlines
        text = "\n".join([str(x) for x in range(0, 10)]) + "\n"
        code = TextCode(text, "plain")

        # Indexes
        self.assertEqual("0\n", code[0])
        self.assertEqual("9\n", code[-1])

        # Slices
        result = code[0:2]
        self.assertEqual("0\n", result[0])
        self.assertEqual("1\n", result[1])

    def test_folding(self):
        # Sample text numbers 1-10 separated by newlines
        text = "\n".join([str(x) for x in range(0, 10)]) + "\n"
        code = TextCode(text, "plain")

        # Fold lines 2 through 9
        code.fold(1, 8)

        self.assertEqual("0\n", code[0])
        self.assertEqual("⠇\n", code[1])
        self.assertIsNone(code[2])
        self.assertIsNone(code[8])
        self.assertEqual("9\n", code[-1])

        # Unfold
        code.unfold(1)
        self.assertEqual("1\n", code[1])
        self.assertEqual("2\n", code[2])

        # Multiple folds
        code.fold(1, 1)
        code.fold(5, 2)
        self.assertEqual("0\n", code[0])
        self.assertEqual("⠇\n", code[1])
        self.assertEqual("2\n", code[2])
        self.assertEqual("⠇\n", code[5])
        self.assertIsNone(code[6])
        self.assertEqual("7\n", code[7])
        self.assertEqual("9\n", code[-1])

        # Unfold when multi-folded
        code.unfold(1)
        self.assertEqual("0\n", code[0])
        self.assertEqual("⠇\n", code[5])
        self.assertIsNone(code[6])
        self.assertEqual("7\n", code[7])

        # Error handling, double-fold
        with self.assertRaises(ValueError):
            code.fold(6, 1)

    def test_wrapping(self):
        path = (Path(__file__).parent / Path("data/wrap.py")).resolve()
        code = Code(path)

        # Default, no wrapping case
        expected = [code.lines[0]]
        result = code.wrap_line(0)
        self.assertEqual(expected, result)

        # Test wrapping at different places.
        #
        # wrap.py line 3:
        #
        # if (alpha == 3 or alpha == "a long string") and beta == 5:
        #                    |              ^=35                |
        #                    ^=20              ^=split + 20     ^=split + 20

        # Wrap once on the space at point 35
        code.wrap = 35
        result = code.wrap_line(2)
        self.assertEqual(2, len(result))
        self.assertEqual("a long ", result[0].parts[-1].text)
        self.assertEqual("string", result[1].parts[0].text)

        # Wrap once midword at point 37
        code.wrap = 37
        result = code.wrap_line(2)
        self.assertEqual(2, len(result))
        self.assertEqual("a long ", result[0].parts[-1].text)
        self.assertEqual("string", result[1].parts[0].text)

        # Wrap twice at size 20
        code.wrap = 20
        result = code.wrap_line(2)
        self.assertEqual(4, len(result))
        self.assertEqual(" ", result[0].parts[-1].text)
        self.assertEqual("alpha", result[1].parts[0].text)
        self.assertEqual("a long ", result[1].parts[-1].text)
        self.assertEqual("string", result[2].parts[0].text)
        self.assertEqual("==", result[2].parts[-1].text)
        self.assertEqual(" ", result[3].parts[0].text)

        # Test full handling of plain.Code
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        code = Code(path)
        code.wrap = 35

        result = "".join(code)
        self.assertEqual(WRAPPED_SIMPLE, result)

    def test_line_numbers(self):
        text = "\n".join(["a" for x in range(0, 1001)]) + "\n"
        code = TextCode(text, "plain")

        # Line numbers off
        self.assertEqual("", code.line_number(0))

        # Starting at 1 (default)
        code.enable_line_numbers = True
        self.assertEqual("   1 ", code.line_number(0))
        self.assertEqual("1001 ", code.line_number(1000))

        # Starting at 10
        code.starting_line_number = 10
        self.assertEqual("  10 ", code.line_number(0))
        self.assertEqual("1010 ", code.line_number(1000))

        # Starting at 9_000
        code.starting_line_number = 9000
        self.assertEqual(" 9000 ", code.line_number(0))
        self.assertEqual("10000 ", code.line_number(1000))

        # Gap
        self.assertEqual("      ", code.line_number_gap())

        # Test full handling of plain.Code
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        code = Code(path)
        code.enable_line_numbers = True
        code.starting_line_number = 8

        result = "".join(code)
        self.assertEqual(NUMBERED_SIMPLE, result)

    def test_highlighting(self):
        text = "zero\none\ntwo\nthree and a bit\nfour and a bit"
        code = TextCode(text, "plain")

        # Int index
        code.highlight(1)
        self.assertEqual(set([1]), code.highlighting)
        code.highlight_all_off()

        # Negative index
        code.highlight(-1)
        self.assertEqual(set([4]), code.highlighting)
        code.highlight_all_off()

        # Tuple (start, length)
        code.highlight( (1, 3) )
        self.assertEqual(set([1, 2, 3]), code.highlighting)
        code.highlight_all_off()

        # Tuple (negative, length)
        code.highlight( (-2, 2) )
        self.assertEqual(set([3, 4]), code.highlighting)
        code.highlight_all_off()

        # String range
        code.highlight("0-2")
        self.assertEqual(set([0, 1]), code.highlighting)
        code.highlight_all_off()

        # Partial Highlighting
        code.highlight("3:6,3")
        self.assertEqual({3:(6, 3)}, code.partial_highlighting)
        code.highlight_all_off()

        # Partial Highlighting, negative index
        code.highlight("-1:5,3")
        self.assertEqual({4:(5, 3)}, code.partial_highlighting)
        code.highlight_all_off()

        # Mixed
        code.highlight(0, -1, "3:10,1")
        self.assertEqual(set([0, 4]), code.highlighting)
        self.assertEqual({3:(10, 1)}, code.partial_highlighting)

        # --- Test Highlight Off
        code.highlight_all_off() # start empty

        # Int
        code.highlight(1)
        code.highlight_off(1)
        self.assertEqual(set(), code.highlighting)

        # Negative Int
        code.highlight(-1)
        code.highlight_off(-1)
        self.assertEqual(set(), code.highlighting)

        # Tuple (start, length)
        code.highlight( (3, 2) )
        code.highlight_off( (3, 2) )
        self.assertEqual(set(), code.highlighting)

        # Tuple (negative start, length)
        code.highlight( (-1, 1) )
        code.highlight_off( (-1, 1) )
        self.assertEqual(set(), code.highlighting)

        # String range, and goes past limit
        code.highlight("0-2")
        code.highlight_off("0-4")
        self.assertEqual(set(), code.highlighting)

        # Error handling: rejects partial
        with self.assertRaises(ValueError):
            code.highlight_off("0:1,4")
