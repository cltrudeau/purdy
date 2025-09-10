from unittest import TestCase

from pygments.token import Generic

from purdy.content import Code
from purdy.parser import token_is_a
from purdy.typewriter import (code_typewriterize, string_typewriterize,
    textual_typewriterize)

# =============================================================================

CODE = """\
if x == 3:    # Comment
    return 4
"""

CONSOLE = """\
>>> x
This is a whole
bunch of output text
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
        result = code_typewriterize(source)

        # Should get back 21 Code objects for the characters in the parsed
        # code, spot check certain aspects to make sure it worked
        self.assertEqual(21, len(result))
        self._spot_check_contents(result)

        # --- Do it again, this time not skipping comments or whitespace
        result = code_typewriterize(source, skip_comments=False,
            skip_whitespace=False)

        # Should get back 35 Code objects, one for each character
        self.assertEqual(35, len(result))
        self._spot_check_contents(result)

    def test_typewriter_console(self):
        source = Code.text(CONSOLE, "repl")

        result = code_typewriterize(source)

        # Console example has a prompt and two output lines, so there should
        # only be 3 Code objects as a result
        self.assertEqual(3, len(result))

        # Spot check some of the contents, first Code obj should have one line
        # with the prompt in it
        self.assertEqual(1, len(result[0].lines))
        self.assertEqual(">>> ", result[0].lines[0].parts[0].text)

        # Second Code obj shouldn't have any output in it
        self.assertEqual(1, len(result[1].lines))

        # Last Code obj should have three lines two of which are Output
        self.assertEqual(3, len(result[2].lines))
        self.assertTrue(
            token_is_a(result[2].lines[1].parts[0].token, Generic.Output))
        self.assertTrue(
            token_is_a(result[2].lines[2].parts[0].token, Generic.Output))

#    def test_textual_typewriter(self):
#        results = textual_typewriterize("one [blue]two[/] three")
#        for item in results:
#            print(item)

#    def test_string_typewriter(self):
#        results = string_typewriterize("one two three")
#        for item in results:
#            print(item)
