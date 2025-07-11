from pathlib import Path
from unittest import TestCase

from purdy.utils import CodeCleaner, TextCodeCleaner

# ===========================================================================
# Result Constants
# ===========================================================================

WITHOUT_DOUBLES = """\
one

two

three

four

five below whitespace line
"""

WITHOUT_DOUBLES_WHITESPACE = """\
one

two

three

four

    
five below whitespace line
"""

FLUSHED = """\
one
    two
        three
    four
five
"""

# =============================================================================

class TestCleaners(TestCase):
    # Test CodeCleaner which calls TextCodeCleaner for everything

    def test_remove_double(self):
        path = (Path(__file__).parent / Path("data/doubles.txt")).resolve()

        # Whitespace is considered a blank line, testing with a Path object
        result = CodeCleaner.remove_double_blanks(path)
        self.assertEqual(WITHOUT_DOUBLES, result)

        # Do it again but with the filename instead of a Path
        result = CodeCleaner.remove_double_blanks(str(path))
        self.assertEqual(WITHOUT_DOUBLES, result)

        # Whitespace NOT a blank line, testing with a Path object
        result = CodeCleaner.remove_double_blanks(path, False)
        self.assertEqual(WITHOUT_DOUBLES_WHITESPACE, result)

        # Do it again but with the filename instead of a Path
        result = CodeCleaner.remove_double_blanks(str(path), False)
        self.assertEqual(WITHOUT_DOUBLES_WHITESPACE, result)

    def test_flush_left(self):
        path = (Path(__file__).parent / Path("data/flush.txt")).resolve()

        # Test with Path object
        result = CodeCleaner.flush_left(path)
        self.assertEqual(FLUSHED, result)

        # Do it again but with the filename instead of a Path
        result = CodeCleaner.flush_left(str(path))
        self.assertEqual(FLUSHED, result)

        # No identing at all
        expected = "one\ntwo\nthree\n"
        result = TextCodeCleaner.flush_left(expected)
        self.assertEqual(expected, result)

        # No flushing needed
        expected = "one\n   two\n   three\n"
        result = TextCodeCleaner.flush_left(expected)
        self.assertEqual(expected, result)

        # Empty string doesn't blow up
        result = TextCodeCleaner.flush_left("")
        self.assertEqual("", result)
