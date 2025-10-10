from unittest import TestCase

from purdy.content import Code, Document, RenderState
from purdy.parser import CURSOR_CHAR
from purdy.tui.tui_content import EscapeText, TextSection
from purdy.tui.typewriter import code_typewriterize, textual_typewriterize

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
        # First TypewriterOutput has one line, last has two
        self.assertEqual(1, result[0].text.plain.count("\n"))
        self.assertEqual(2, result[-1].text.plain.count("\n"))

        # First TypewriterOutput has the letter "i" from "if", the CURSOR, and
        # a newline
        value = result[0].text.plain
        self.assertEqual(3, len(value))
        self.assertEqual("i", value[0])
        self.assertEqual(CURSOR_CHAR, value[1])

        # Last TypewriterOutput's second line is:
        #
        # if x == 3:    # Comment\n    return 4█\n
        # 0123456789^123456789^123456789^123456789
        #
        value = result[-1].text.plain
        self.assertEqual(38, len(value))
        self.assertEqual("return", value[28:34])

    def test_typewriter(self):
        code = Code.text(CODE)
        doc = Document(code)
        rs = RenderState(doc)

        # Test with skipping comments and whitespace
        result = code_typewriterize(rs, code)

        # Should get back 21 TypewriterOutput objects for the characters in
        # the parsed code, spot check certain aspects to make sure it worked
        self.assertEqual(21, len(result))
        self._spot_check_contents(result)

        # --- Do it again, this time not skipping comments or whitespace
        result = code_typewriterize(rs, code, skip_comments=False,
            skip_whitespace=False)

        # Should get back 35 TypwriterOutput objects, one for each character
        self.assertEqual(35, len(result))
        self._spot_check_contents(result)

    def test_typewriter_console(self):
        code = Code.text(CONSOLE, "repl")
        doc = Document(code)
        rs = RenderState(doc)

        result = code_typewriterize(rs, code)

        # Console example has a prompt and two output lines, so there should
        # only be 4 TypewriterOutput objects as a result, the last two both
        # having no pause state
        self.assertEqual(4, len(result))
        self.assertEqual(None, result[-1].state)
        self.assertEqual(None, result[-2].state)

        # Spot check some of the contents, first TypewriterOutput obj should
        # have one line with the prompt and cursor in it
        value = result[0].text.plain
        self.assertEqual(6, len(value))
        self.assertEqual(">>> ", value[:4])

        # Second TypewriterOutput obj shouldn't have any output in it
        value = result[1].text.plain
        self.assertEqual(1, value.count("\n"))

        # Last TypewriterOutput obj should have all the content
        expected = ">>> x\nThis is a whole\nbunch of output text\n"
        value = result[-1].text.plain
        self.assertEqual(expected, value)

    def test_typewriter_bash(self):
        code = Code.text("$ pgm\noutput", "con")
        doc = Document(code)
        rs = RenderState(doc)

        result = code_typewriterize(rs, code)

        # Console has a prompt and one output lines, should be 5
        # TypewriterOutput objects for the program and the output, waiting
        # after the initial line with the prompt, pausing to type the program
        # name, then not pausing at the output
        self.assertEqual(5, len(result))
        self.assertEqual("W", result[0].state)
        self.assertEqual("P", result[1].state)
        self.assertEqual(None, result[-1].state)

        # Test multi-part prompts
        code = Code.text("(venv) $ thing\nstuff", "con")
        doc = Document(code)
        rs = RenderState(doc)

        result = code_typewriterize(rs, code)

        # Prompt has a VirtualEnv part, all that needs to have been merged
        # into a single thing
        self.assertEqual(7, len(result))
        self.assertIn("(venv) $ ", result[0].text.plain)
        self.assertEqual("W", result[0].state)
        self.assertIn("(venv) $ t", result[1].text.plain)
        self.assertEqual("P", result[1].state)
        self.assertEqual(None, result[-1].state)

    def test_textual_typewriter(self):
        section = TextSection()
        plain = "plain [escaped] string\n"
        section.lines.append(EscapeText(plain))
        section.lines.append("textual [blue]markup[/] string")

        doc = Document(section)
        rs = RenderState(doc)

        results = textual_typewriterize(rs, section)
        self.assertEqual(46, len(results))

        # First part of section is the escaped text, starts with "p"
        value = results[0].text.plain
        self.assertEqual("p", value[0])

        # Achieves full line in TypewriterObject #22
        expected = plain + CURSOR_CHAR
        value = results[22].text.plain
        self.assertEqual(expected, value)

        # Check the final result that has textual markup in it
        expected = "plain [escaped] string\ntextual markup string" + CURSOR_CHAR
        value = results[-1].text.plain
        self.assertEqual(expected, value)
