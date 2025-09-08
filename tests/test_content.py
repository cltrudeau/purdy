from copy import deepcopy
from pathlib import Path
from unittest import TestCase

from purdy.content import Code, MultiCode

# =============================================================================

class TestCode(TestCase):
    def test_code_factories(self):
        text = "\n".join([str(x) for x in range(0, 10)]) + "\n"

        # Constructor as factory
        path = (Path(__file__).parent / Path("data/count.txt")).resolve()
        code = Code(path, "plain")

        self.assertEqual(10, len(code.lines))
        self.assertEqual("0", code.lines[0].parts[0].text)
        self.assertEqual("9", code.lines[9].parts[0].text)

        # Text based factory
        code = Code.text(text, "plain")

        self.assertEqual(10, len(code.lines))
        self.assertEqual("0", code.lines[0].parts[0].text)
        self.assertEqual("9", code.lines[9].parts[0].text)

        # Spawn
        spawn = code.spawn()
        self.assertEqual(code.parser, spawn.parser)
        self.assertEqual(0, len(spawn.lines))

    def test_chunk(self):
        text = "\n".join([str(x) for x in range(0, 5)]) + "\n"
        code = Code.text(text, "plain")

        expected_lines = deepcopy(code.lines[0:3])
        result = code.chunk(3)
        self.assertEqual(expected_lines, result.lines)

        expected_lines = deepcopy(code.lines[3:5])
        result = code.chunk(3)
        self.assertEqual(expected_lines, result.lines)

        result = code.chunk(3)
        self.assertEqual([], result.lines)

    def test_folding(self):
        # Sample text numbers 1-10 separated by newlines
        text = "\n".join([str(x) for x in range(0, 10)]) + "\n"
        code = Code.text(text, "plain")

        # Fold lines 2 through 9
        code.fold(1, 8)

        # Folding line[1], length=8 means that eight items of metadata get
        # created, validate that nothing else got created accidentally
        self.assertEqual(8, len(code.meta))
        self.assertTrue(code.meta[1].folded)
        self.assertFalse(code.meta[1].hidden)

        for x in range(2, 9):
            self.assertFalse(code.meta[x].folded)
            self.assertTrue(code.meta[x].hidden)

        # Unfold
        code.unfold(1)

        # Unfolding doesn't remove the metadata, but want to make sure nothing
        # new was added
        self.assertEqual(8, len(code.meta))

        self.assertFalse(code.meta[1].folded)
        self.assertFalse(code.meta[1].hidden)

        for x in range(2, 9):
            self.assertFalse(code.meta[x].folded)
            self.assertFalse(code.meta[x].hidden)

        # Multiple folds
        code.reset_metadata()
        code.fold(1, 1)
        code.fold(5, 2)

        # Two folds and one hidden
        self.assertEqual(3, len(code.meta))

        self.assertTrue(code.meta[1].folded)
        self.assertFalse(code.meta[1].hidden)

        self.assertTrue(code.meta[5].folded)
        self.assertFalse(code.meta[5].hidden)

        self.assertFalse(code.meta[6].folded)
        self.assertTrue(code.meta[6].hidden)

        # Unfold when multi-folded
        code.unfold(1)
        self.assertEqual(3, len(code.meta))

        self.assertFalse(code.meta[1].folded)
        self.assertFalse(code.meta[1].hidden)

        # Error handling, double-fold
        with self.assertRaises(ValueError):
            code.fold(6, 1)

        # Make sure all this mucking about hasn't created unnecessary sparse
        # entries
        self.assertEqual(3, len(code.meta))

        # Error handling, unfold something not folded
        code.reset_metadata()
        with self.assertRaises(ValueError):
            code.unfold(0)

    def test_highlight_activation(self):
        text = "zero\none\ntwo\nthree and a bit\nfour and a bit"
        code = Code.text(text, "plain")

        # Int index
        code.highlight(1)
        self.assertTrue(code.meta[1].highlight)
        code.reset_metadata()

        # Negative index
        code.highlight(-1)
        self.assertTrue(code.meta[4].highlight)
        code.reset_metadata()

        # Tuple (start, length)
        code.highlight( (1, 3) )
        self.assertTrue(code.meta[1].highlight)
        self.assertTrue(code.meta[2].highlight)
        self.assertTrue(code.meta[3].highlight)
        code.reset_metadata()

        # Tuple (negative, length)
        code.highlight( (-2, 2) )
        self.assertTrue(code.meta[3].highlight)
        self.assertTrue(code.meta[4].highlight)
        code.reset_metadata()

        # String int
        code.highlight("0")
        self.assertTrue(code.meta[0].highlight)
        code.reset_metadata()

        # String int negative
        code.highlight("-1")
        self.assertTrue(code.meta[4].highlight)
        code.reset_metadata()

        # String range
        code.highlight("0-2")
        self.assertTrue(code.meta[0].highlight)
        self.assertTrue(code.meta[1].highlight)
        self.assertTrue(code.meta[2].highlight)
        code.reset_metadata()

        # Partial Highlighting
        code.highlight("3:6,3")
        self.assertEqual( [(6, 3)], code.meta[3].highlight_partial)
        code.reset_metadata()

        # Partial Highlighting, negative index
        code.highlight("-1:5,3")
        self.assertEqual( [(5, 3)], code.meta[4].highlight_partial)
        code.reset_metadata()

        # Mixed
        code.highlight(0, -1, "3:10,1")
        self.assertTrue(code.meta[0].highlight)
        self.assertTrue(code.meta[4].highlight)
        self.assertEqual( [(10, 1)], code.meta[3].highlight_partial)
        code.reset_metadata()

        # --- Test Highlight Off
        # Int
        code.highlight(1)
        code.highlight_off(1)
        self.assertEqual(1, len(code.meta))
        self.assertFalse(code.meta[1].highlight)
        code.reset_metadata()

        # Negative Int
        code.highlight(-1)
        code.highlight_off(-1)
        self.assertEqual(1, len(code.meta))
        self.assertFalse(code.meta[4].highlight)
        code.reset_metadata()

        # Tuple (start, length)
        code.highlight( (3, 2) )
        code.highlight_off( (3, 2) )
        self.assertEqual(2, len(code.meta))
        self.assertFalse(code.meta[3].highlight)
        self.assertFalse(code.meta[4].highlight)
        code.reset_metadata()

        # Tuple (negative start, length)
        code.highlight( (-1, 1) )
        code.highlight_off( (-1, 1) )
        self.assertEqual(1, len(code.meta))
        self.assertFalse(code.meta[4].highlight)
        code.reset_metadata()

        # String range, and goes past limit
        code.highlight("0-2")
        code.highlight_off("0-4")

        self.assertEqual(5, len(code.meta))
        for i in range(0, 5):
            self.assertFalse(code.meta[i].highlight)

        code.reset_metadata()

        # All off
        code.highlight("0-2")
        code.highlight_all_off()

        self.assertEqual(3, len(code.meta))
        for i in range(0, 3):
            self.assertFalse(code.meta[i].highlight)

        # Error handling: rejects partial
        with self.assertRaises(ValueError):
            code.highlight_off("0:1,4")


class TestMultiCode(TestCase):
    def test_multicode_init(self):
        mc = MultiCode()
        self.assertEqual(0, len(mc))

        text = "one"
        code1 = Code.text(text, "plain")

        mc = MultiCode(code1)
        self.assertEqual(1, len(mc))
        self.assertEqual(code1, mc[0])

        text = "two"
        code2 = Code.text(text, "plain")

        mc = MultiCode([code1, code2])
        self.assertEqual(2, len(mc))
        self.assertEqual(code1, mc[0])
        self.assertEqual(code2, mc[1])

    def test_line_numbers(self):
        text = "\n".join(["a" for x in range(0, 500)]) + "\n"
        code1 = Code.text(text, "plain")

        text = "\n".join(["a" for x in range(500, 1001)]) + "\n"
        code2 = Code.text(text, "plain")

        mc = MultiCode([code1, code2])

        # Line numbers off
        self.assertEqual("", mc.line_number(0, 0))
        self.assertEqual("", mc.line_number_gap())

        # Starting at 1 (default)
        mc.line_numbers_enabled = True
        self.assertEqual("   1 ", mc.line_number(0, 0))
        self.assertEqual("1001 ", mc.line_number(1, 500))

        # Starting at 10
        mc.starting_line_number = 10
        self.assertEqual("  10 ", mc.line_number(0, 0))
        self.assertEqual("1010 ", mc.line_number(1, 500))

        # Starting at 9_000
        mc.starting_line_number = 9000
        self.assertEqual(" 9000 ", mc.line_number(0, 0))
        self.assertEqual("10000 ", mc.line_number(1, 500))

        # Gap
        self.assertEqual("      ", mc.line_number_gap())
