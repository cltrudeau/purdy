from copy import deepcopy
from pathlib import Path
from unittest import TestCase

from purdy.content import Code, Document, PyText, RenderState, StringSection
from purdy.parser import HighlightOn, HighlightOff, token_is_a
from purdy.renderers.plain import to_plain

# =============================================================================
# Result Constants
# =============================================================================

WRAP_SIMPLE = "\n".join([
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

NUM_SIMPLE = "\n".join([
    r' 8 # Small file for simple parser testing',
    r' 9 def simple(thing):',
    r'10     """This tests',
    r'11     multi-line strings"""',
    r'12     return thing + "\nDone"',
    r'13 ',
    r'14 simple("A string\nWith newline")',
    r'',
])

WRAP_NUM_SIMPLE = "\n".join([
    r' 8 # Small file for simple parser ',
    r'testing',
    r' 9 def simple(thing):',
    r'10     """This tests',
    r'11     multi-line strings"""',
    r'12     return thing + "\nDone"',
    r'13 ',
    r'14 simple("A string\nWith newline")',
    r'',
])

WRAP_BIG_NUM_SIMPLE = "\n".join([
    r'10000 # Small file for simple ',
    r'parser testing',
    r'10001 def simple(thing):',
    r'10002     """This tests',
    r'10003     multi-line strings"""',
    r'10004     return thing + "\nDone"',
    r'10005 ',
    r'10006 simple("A string\nWith ',
    r'newline")',
    r'',
])

WRAP_FOLD_BIG_NUM_SIMPLE = "\n".join([
    r'10000 # Small file for simple ',
    r'parser testing',
    r'10001 def simple(thing):',
    r"10002 ⠇",
    r'10005 ',
    r'10006 simple("A string\nWith ',
    r'newline")',
    r'',
])

# =============================================================================

class BraceFormatter:
    ### Text based formatter that marks highlights with special characters
    def render_code_line(self, render_state, line):
        result = ""
        for part in line.parts:
            if token_is_a(part.token, HighlightOn):
                result += "{"
            elif token_is_a(part.token, HighlightOff):
                result += "}"
            else:
                result += part.text

        if line.has_newline:
            result += "\n"

        render_state.content += result

# =============================================================================

PYTEXT_SRC = """\
# Header
def print_name(name):
    # Comment
    print(name)

class Car:
    def drive(self):
        print("Vroom")
"""

JUSTIFIED = """\
one
    two
        three
"""

JUSTIFY1 = """\
        one
            two
                three
"""

class TestPyText(TestCase):
    def test_portion(self):
        # test finding a function
        original = PyText.text(PYTEXT_SRC)
        part = original.get_part("print_name")

        lines = part.content.splitlines()
        self.assertEqual("def print_name(name):", lines[0])
        self.assertEqual("    print(name)", lines[-1])

        # test find a function with an integer header
        part = original.get_part("Car", header=1)
        lines = part.content.splitlines()
        self.assertEqual("# Header", lines[0])
        self.assertEqual('        print("Vroom")', lines[-1])

        # test find a function with a tuple header
        part = original.get_part("Car", header=(1, 3))
        lines = part.content.splitlines()
        self.assertEqual("def print_name(name):", lines[0])
        self.assertEqual("    # Comment", lines[1])
        self.assertEqual("class Car:", lines[2])
        self.assertEqual('        print("Vroom")', lines[-1])

    def test_left_justify(self):
        original = PyText.text(JUSTIFY1)
        result = original.left_justify()
        self.assertEqual(JUSTIFIED, result.content)

    def test_remove_double_blanks(self):
        text = "one\n\ntwo\nthree\n  \n  \nfour"

        # Trim whitespace
        original = PyText.text(text)
        result = original.remove_double_blanks()
        self.assertEqual("one\n\ntwo\nthree\n  \nfour", result.content)

        # Don't trim whitespace
        text = "one\n\n\ntwo\n  \nthree"
        original = PyText.text(text)
        result = original.remove_double_blanks(trim_whitespace=False)
        self.assertEqual("one\n\ntwo\n  \nthree", result.content)

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

        # Slice access
        result = code[0:2]
        self.assertEqual(2, len(result.lines))
        self.assertEqual("0", result.lines[0].parts[0].text)
        self.assertEqual("1", result.lines[1].parts[0].text)

        result = code[1]
        self.assertEqual(1, len(result.lines))
        self.assertEqual("1", result.lines[0].parts[0].text)


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

        # Remaining chunk
        code.current = 0
        _ = code.chunk(3)
        expected_lines = deepcopy(code.lines[3:5])
        result = code.remaining_chunk()
        self.assertEqual(expected_lines, result.lines)

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

    def test_highlight(self):
        # Tests the meta data portion of highlighting
        text = "zero\none\ntwo\nthree and a bit\nfour and a bit"
        code = Code.text(text, "plain")

        # Int index
        code.highlight(1)
        self.assertTrue(code.meta[1].highlight)
        self.assertTrue(code.is_highlighted(1))
        self.assertFalse(code.is_highlighted(2))
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
        self.assertTrue(code.is_highlighted(3))
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

        # Partial Highlighting
        code.highlight("3:6,3")
        code.highlight_off("3:6,3")
        self.assertEqual(1, len(code.meta))
        self.assertEqual([], code.meta[3].highlight_partial)
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

        # Error handling: rejects partial that isn't on
        with self.assertRaises(ValueError):
            code.highlight_off("0:1,4")

    def test_apply_highlight(self):
        # Tests the token manipulation portion of highlighted lines
        text = "zero\none\ntwo\nthree and a bit\nfour and a bit"
        code = Code.text(text, "plain")

        # Make sure to test highlight length of 1, it was problematic before
        code.highlight(2, "3:6,3", "4:0,1")

        # No highlighting
        line = code._apply_highlight(0)
        self.assertEqual(line, code.lines[0])

        # Full line
        line = code._apply_highlight(2)
        self.assertTrue(token_is_a(line.parts[0].token, HighlightOn))
        self.assertTrue(token_is_a(line.parts[-1].token, HighlightOff))

        # Partial line, "and" in "three and a bit"
        line = code._apply_highlight(3)
        self.assertTrue(token_is_a(line.parts[1].token, HighlightOn))
        self.assertTrue(token_is_a(line.parts[3].token, HighlightOff))

        # Partial line, "f" in "four and a bit"
        line = code._apply_highlight(4)
        self.assertTrue(token_is_a(line.parts[0].token, HighlightOn))
        self.assertTrue(token_is_a(line.parts[2].token, HighlightOff))

    def test_arg_highlight(self):
        # Test highlighting based on argument number

        #         0123456789^123456789^123456789^123456
        text = """def fn(1, "hello", cat='tiger', True)"""
        code = Code.text(text)

        # Get partial indexing for first argument (zero-index)
        index, (start, length) = code._parse_partial("0:arg:0")
        self.assertEqual(0, index)
        self.assertEqual("1", text[start:start+length])

        # Get partial indexing info for the 3rd argument
        index, (start, length) = code._parse_partial("0:arg:2")
        self.assertEqual(0, index)
        self.assertEqual("cat='tiger'", text[start:start+length])

        # Get partial indexing info for last argument
        index, (start, length) = code._parse_partial("0:arg:3")
        self.assertEqual(0, index)
        self.assertEqual("True", text[start:start+length])

        # Validate error handling
        with self.assertRaises(ValueError):
            code._parse_partial("0:arg:4")

        text = "x = 1"
        code = Code.text(text)
        with self.assertRaises(ValueError):
            code._parse_partial("0:arg:0")

    def test_render_highlight(self):
        text = "zero\none\ntwo\nthree and a bit\nfour and a bit"
        code = Code.text(text, "plain")
        code.highlight(1)
        code.highlight("3:6,3")

        doc = Document(code)
        rs = RenderState(doc)
        rs.formatter = BraceFormatter()

        expected = "zero\n{one}\ntwo\nthree {and} a bit\nfour and a bit"
        doc[0].render(rs)
        self.assertEqual(expected, rs.content)

    def test_wrapping(self):
        path = (Path(__file__).parent / Path("data/wrap.py")).resolve()
        code = Code(path)
        doc = Document(code)

        # Default, no wrapping case
        expected = path.read_text()
        result = to_plain(doc)
        self.assertEqual(expected, result)

        # Test wrapping at different places.
        #
        # wrap.py line 3:
        #
        # if (alpha == 3 or alpha == "a long string") and beta == 5:
        #                    |              ^=35                |
        #                    ^=20              ^=split + 20     ^=split + 20

        # Wrap once on the space at point 35
        doc.wrap = 35
        result = to_plain(doc).split("\n")
        self.assertEqual(6, len(result))
        self.assertEqual("a long ", result[2][-7:])
        self.assertEqual("string", result[3][0:6])

        # Wrap once midword at point 37, should get same result
        doc.wrap = 37
        result = to_plain(doc).split("\n")
        self.assertEqual(6, len(result))
        self.assertEqual("a long ", result[2][-7:])
        self.assertEqual("string", result[3][0:6])

        # Wrap twice at size 20
        doc.wrap = 20
        result = to_plain(doc).split("\n")
        self.assertEqual(8, len(result))
        self.assertEqual("or ", result[2][-3:])
        self.assertEqual("alpha", result[3][0:5])
        self.assertEqual("a long ", result[3][-7:])
        self.assertEqual("string", result[4][0:6])
        self.assertEqual("==", result[4][-2:])
        self.assertEqual(" 5:", result[5])

        # Test really wide wrapping
        code = Code.text("# One two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twenty-one twenty-two twenty-three twenty-four twenty-five\n")
        doc = Document(code)
        doc.wrap = 80
        result = to_plain(doc).split("\n")
        self.assertEqual(4, len(result))
        self.assertEqual("thirteen ", result[0][-9:])
        self.assertEqual("-one ", result[1][-5:])
        self.assertEqual("-five", result[2][-5:])
        self.assertEqual("", result[3])

    def test_render_variations(self):
        # Test full handling of plain.Code
        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        code = Code(path)
        doc = Document(code)
        doc.wrap = 35
        result = to_plain(doc)
        self.assertEqual(WRAP_SIMPLE, result)

        # Test wrapping with numbers
        doc.line_numbers_enabled = True
        doc.starting_line_number = 8
        result = to_plain(doc)
        self.assertEqual(WRAP_NUM_SIMPLE, result)

        # Test wrapping with numbers that bump the wrap point
        doc.starting_line_number = 10_000
        result = to_plain(doc)
        self.assertEqual(WRAP_BIG_NUM_SIMPLE, result)

        # Test wrapping and folding
        code.fold(2, 3)
        doc = Document(code)
        doc.wrap = 35
        doc.line_numbers_enabled = True
        doc.starting_line_number = 10_000
        result = to_plain(doc)
        self.assertEqual(WRAP_FOLD_BIG_NUM_SIMPLE, result)

# =============================================================================

class TestDocument(TestCase):
    def test_document_init(self):
        doc = Document()
        self.assertEqual(0, len(doc))

        text = "one"
        code1 = Code.text(text, "plain")

        doc = Document(code1)
        self.assertEqual(1, len(doc))
        self.assertEqual(code1, doc[0])

        text = "two"
        code2 = Code.text(text, "plain")

        doc = Document([code1, code2])
        self.assertEqual(2, len(doc))
        self.assertEqual(code1, doc[0])
        self.assertEqual(code2, doc[1])

    def test_mixed_content(self):
        doc = Document()
        code = Code.text("one\n", "plain")
        doc.append(code)
        s = StringSection("two\n")
        doc.append(s)
        result = to_plain(doc)
        self.assertEqual("one\ntwo\n", result)

# =============================================================================

class TestRenderState(TestCase):
    def test_line_numbers(self):
        text = "\n".join(["a" for x in range(0, 500)]) + "\n"
        code1 = Code.text(text, "plain")

        text = "\n".join(["a" for x in range(500, 1001)]) + "\n"
        code2 = Code.text(text, "plain")

        doc = Document([code1, code2])
        doc.line_numbers_enabled = True

        # Default, starting at 1
        rs = RenderState(doc)
        self.assertEqual(1, rs.line_number)
        self.assertEqual("   1 ", rs.next_line_number())
        self.assertEqual("   2 ", rs.next_line_number())

        # Starting at 10
        doc.starting_line_number = 10
        rs = RenderState(doc)
        self.assertEqual(10, rs.line_number)
        self.assertEqual("  10 ", rs.next_line_number())
        self.assertEqual("  11 ", rs.next_line_number())

        # Starting at 9_000
        doc.starting_line_number = 9999
        rs = RenderState(doc)
        self.assertEqual(9999, rs.line_number)
        self.assertEqual(" 9999 ", rs.next_line_number())
        self.assertEqual("10000 ", rs.next_line_number())

        # Gap
        self.assertEqual("      ", rs.line_number_gap())
