from unittest.mock import patch, mock_open

from pygments.token import Token
from waelstow import capture_stdout

from purdy.content import Code, Listing

from tests.base import (PurdyContentTest, py3_lexer, bash_lexer, PY_CODE_LINES,
    BASH_CODE_LINES)

# =============================================================================

class TestContent(PurdyContentTest):
    def assert_code_parts(self, line_list, listing):
        # loop through line_list (consists of manually created CodeLine
        # objects) and compare it to the actually parsed code object
        for i, line in enumerate(listing.lines):
            for j, part in enumerate(line.parts):
                expected = line_list[i].parts[j]

                try:
                    self.assertEqual(expected.token, part.token)
                    self.assertEqual(expected.text, part.text)
                except AssertionError as e:
                    raise AssertionError(str(e) + f' CodeLine[{i}]')
                
    def test_content(self):
        # need to test both py3 and bash to get all parsing cases
        code = Code(text=self.py_source, lexer_name='py3')
        listing = Listing(code)
        self.assert_code_parts(PY_CODE_LINES, listing)

        with patch('builtins.open', mock_open(read_data=self.bash_source)):
            code = Code(filename='foo', lexer_name='bash')
            listing = Listing(code)
            self.assert_code_parts(BASH_CODE_LINES, listing)

        # test line numbering
        listing.starting_line_number = 10
        listing.reset_line_numbers(1)
        for count, line in enumerate(listing.lines):
            self.assertEqual(count + 10, line.line_number)
