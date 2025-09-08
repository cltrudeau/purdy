from unittest import TestCase

from purdy.content import Code
from purdy.typewriter import Typewriter

# =============================================================================

CODE = """\
if x == 3:    # Comment
    return 4
"""

class TestTypewriter(TestCase):
    def _spot_check_contents(self, result):
        # First Code object has one line, last has two
        self.assertEqual(1, len(result[0].lines))
        self.assertEqual(2, len(result[-1].lines))

        # First Code object's line has one part, just the letter "i" from "if"
        self.assertEqual(1, len(result[0].lines[0].parts))
        self.assertEqual("i", result[0].lines[0].parts[0].text)

        # Last Code object's second line has four parts: space, return, space,
        # 4
        self.assertEqual(4, len(result[-1].lines[-1].parts))
        self.assertEqual("return", result[-1].lines[1].parts[1].text)

    def test_typewriter(self):
        source = Code.text(CODE)
        #from purdy._debug import print_code_lines
        #print_code_lines(source.lines)

        # Test with skipping comments and whitespace
        result = Typewriter.typewriterize(source)

        # Should get back 21 Code objects for the characters in the parsed
        # code, spot check certain aspects to make sure it worked
        self.assertEqual(21, len(result))
        self._spot_check_contents(result)

        # --- Do it again, this time not skipping comments or whitespace
        result = Typewriter.typewriterize(source, skip_comments=False,
            skip_whitespace=False)

        # Should get back 35 Code objects, one for each character
        self.assertEqual(35, len(result))
        self._spot_check_contents(result)
