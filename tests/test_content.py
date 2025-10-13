from copy import deepcopy
from unittest.mock import patch, mock_open, Mock, call

from pygments.token import Token

from purdy.content import Code, Listing
from purdy.parser import CodeLine, CodePart, FoldedCodeLine

from tests.base import (PurdyContentTest, py3_lexer, PY_CODE_LINES,
    BASH_CODE_LINES)

# =============================================================================

def py_line(text, num=-1):
    line = CodeLine([CodePart(Token.Text, text)], py3_lexer)
    if num > 0:
        line.line_number = num
    return line

def alpha_lines(num):
    # returns "num" code lines, with contents A, B, C...
    return [
        CodeLine([CodePart(Token.Text, chr(x))], py3_lexer) for x in \
            range(65, 65 + num)
    ]

# commented out to hide from pyflakes
#
#def _print_lines(title, lines):
#    # Used to help debug the tests
#    print(f'==== {title} ====')
#    for line in lines:
#        print(line)


class TestContent(PurdyContentTest):
    def assert_code_parts(self, line_list, listing):
        # loop through line_list (consists of manually created CodeLine
        # objects) and compare it to the actually parsed code object
        for i, line in enumerate(listing.lines):
            for j, part in enumerate(line.parts):
                expected = line_list[i].parts[j]

#                print(f"******** {i=} {j=}")
#                print(f"   {expected=}")
#                print(f"   {expected.token=}")
#                print(f"   {part.token=}")
#                print(f"   {expected=}")
#                print(f"   {expected.text=}")
#                print(f"   {part.text=}")

                self.assertEqual(expected.token, part.token,
                    msg=f'Failed for CodeLine[{i}]')
                self.assertEqual(expected.text, part.text,
                    msg=f'Failed for CodeLine[{i}]')

    def assert_line_text(self, expected_text, lines):
        self.assertEqual(len(expected_text), len(lines),
            msg='Size mismatch between expected_text and lines')
        for x, text in enumerate(expected_text):
            self.assertEqual(text, lines[x].parts[0].text,
                msg=f'expected_text[{x}] did not match line')

    def hooked_listing(self, append_code=True):
        mock_hook = Mock()
        listing = Listing(starting_line_number=10)
        listing.set_display('ansi', mock_hook)

        if append_code:
            code = Code(text=self.py_source, lexer_name='py3')
            listing.append_code(code)

        return mock_hook, listing

    #=== Test Methods

    def test_construction(self):
        #---Test construction via a Code object. Need to test both py3 and
        # bash to get all parsing cases
        with patch('builtins.open', mock_open(read_data=self.bash_source)):
            code = Code(filename='foo', lexer_name='bash')
            listing = Listing(code)
            self.assert_code_parts(BASH_CODE_LINES, listing)

        code = Code(text=self.py_source)  # py3 lexer, but let it auto-detect
        listing = Listing(code)
        self.assert_code_parts(PY_CODE_LINES, listing)

        #---Test line numbering
        listing.starting_line_number = 10
        listing.reset_line_numbers()
        for count, line in enumerate(listing.lines):
            self.assertEqual(count + 10, line.line_number)

        #---Test lists of Code 
        listing = Listing([code, code])
        self.assertEqual(2 * len(PY_CODE_LINES), len(listing.lines))

    def test_setters(self):
        mock_hook, listing = self.hooked_listing()

        new_lines = [py_line('foo'), py_line('bar')]

        #--- Create a new listing, append code and check render hook was called
        calls = [ call(listing, i+1, line) for i, line in \
            enumerate(listing.lines)]
        mock_hook.line_inserted.assert_has_calls(calls)

        # Test mid insertion 
        size = len(listing.lines)
        mock_hook.reset_mock()
        listing.insert_lines(2, new_lines)

        self.assertEqual(py_line('foo', 11), listing.lines[1])
        self.assertEqual(py_line('bar', 12), listing.lines[2])
        self.assertEqual(size + 2, len(listing.lines))

        calls = [ 
            call(listing, 2, listing.lines[1]), 
            call(listing, 3, listing.lines[2])
        ]
        mock_hook.line_inserted.assert_has_calls(calls)

        # ensure line numbering got reset
        for count, line in enumerate(listing.lines):
            self.assertEqual(count + 10, line.line_number)

        # ensure the change call was made for the lines whose numbers changed
        calls = []
        for x in range(3, len(listing.lines)):
            calls.append( call(listing, x + 1, listing.lines[x]) )
        mock_hook.line_changed.assert_has_calls(calls)

        #--- Test negative position insertion
        size = len(listing.lines)
        mock_hook.reset_mock()

        listing.insert_lines(-1, new_lines)

        calls = [ 
            call(listing, size, listing.lines[-3]), 
            call(listing, size + 1, listing.lines[-2])
        ]
        mock_hook.line_inserted.assert_has_calls(calls)

        self.assertEqual(size + 2, len(listing.lines))
        self.assertEqual(py_line('foo', 18), listing.lines[-3])
        self.assertEqual(py_line('bar', 19), listing.lines[-2])

        #--- Test replacement
        size = len(listing.lines)
        mock_hook.reset_mock()
        replace_line = py_line('waz')

        listing.replace_line(-1, replace_line)

        mock_hook.line_changed.assert_called_once_with(listing, size,
            listing.lines[-1])

        self.assertEqual(size, len(listing.lines))
        self.assertEqual(py_line('waz', 20), listing.lines[-1])

    def test_remove(self):
        mock_hook, listing = self.hooked_listing()

        expected = deepcopy(listing.lines)
        del expected[1]
        del expected[1]
        for count, line in enumerate(expected):
            line.line_number = 10 + count

        listing.remove_lines(2, 2)
        self.assertEqual(expected, listing.lines)

        # Verify removal hooks
        calls = [ 
            call(listing, 2),
            call(listing, 2),
        ]
        mock_hook.line_removed.assert_has_calls(calls)

        # Check lines were renumbered
        listing.starting_line_number = 10
        for count, line in enumerate(listing.lines):
            self.assertEqual(count + 10, line.line_number)

        # ensure the change call was made for the lines whose numbers changed
        calls = []
        for x in range(1, len(listing.lines)):
            calls.append( call(listing, x + 1, listing.lines[x]) )
        mock_hook.line_changed.assert_has_calls(calls)

    def test_clear(self):
        mock_hook, listing = self.hooked_listing()

        listing.clear()
        self.assertEqual(0, len(listing.lines))
        mock_hook.clear.assert_called_once()

    def test_highlight(self):
        mock_hook, listing = self.hooked_listing()

        listing.set_highlight(True, 2, 3)
        for count, line in enumerate(listing.lines):
            if count in (1, 2):
                self.assertTrue(line.highlight)
            else:
                self.assertFalse(line.highlight)

        listing.set_highlight(False, 1)
        for count, line in enumerate(listing.lines):
            self.assertFalse(line.highlight)

    def test_content(self):
        code = Code(text=self.py_source, lexer_name='py3')
        listing = Listing(code, starting_line_number=10)

        result = listing.content()
        for count, line in enumerate(listing.lines):
            self.assertEqual(result[count], f'{count+10:3} ' + line.text)

    def test_insert_lines(self):
        ### Test insert with various positions

        # Empty and 0
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(1))
        self.assertEqual(1, len(listing.lines))

        # One line and 0
        listing.insert_lines(0, [py_line('B'), ])
        self.assertEqual(2, len(listing.lines))
        self.assert_line_text('AB', listing.lines)

        # Three lines and -1
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(3))

        listing.insert_lines(-1, [py_line('Z'), ])
        self.assert_line_text('ABZC', listing.lines)

        # Inserting multiple midway
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(3))

        listing.insert_lines(2, [ py_line('X'), py_line('Y'), py_line('Z'), ])
        self.assert_line_text('AXYZBC', listing.lines)

        # Boundary tests
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(1))

        with self.assertRaises(IndexError):
            listing.insert_lines(-10, [py_line('Z'), ])

        with self.assertRaises(IndexError):
            listing.insert_lines(100, [py_line('Z'), ])

    def test_replace_line(self):
        ### Test replace with various positions

        # One line and 1
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(1))
        listing.replace_line(1, py_line('Z'))
        self.assert_line_text('Z', listing.lines)

        # One line and -1
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(1))
        listing.replace_line(-1, py_line('Z'))
        self.assert_line_text('Z', listing.lines)

        # Three lines and 2 
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(3))
        listing.replace_line(2, py_line('Z'))
        self.assert_line_text('AZC', listing.lines)

        # Three lines and -2
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(3))
        listing.replace_line(-2, py_line('Z'))
        self.assert_line_text('AZC', listing.lines)

        # Boundary test
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(1))

        with self.assertRaises(IndexError):
            listing.replace_line(0, py_line('Z'))

        with self.assertRaises(IndexError):
            listing.replace_line(-10, py_line('Z'))

        with self.assertRaises(IndexError):
            listing.replace_line(100, py_line('Z'))

    def test_remove_lines(self):
        ### Test remove with various positions

        # Two lines, remove @ 1
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(2))
        listing.remove_lines(1)
        self.assert_line_text('B', listing.lines)

        # Three lines, remove @ 2 
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(3))
        listing.remove_lines(2)
        self.assert_line_text('AC', listing.lines)

        # Three lines and -2
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(3))
        listing.remove_lines(-2)
        self.assert_line_text('AC', listing.lines)

        #---Remove multiple lines

        # from top
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(4))
        listing.remove_lines(1, 2)
        self.assert_line_text('CD', listing.lines)

        # from middle
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(4))
        listing.remove_lines(-3, 2)
        self.assert_line_text('AD', listing.lines)

        #---Boundary test
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(1))

        with self.assertRaises(IndexError):
            listing.remove_lines(0)

        with self.assertRaises(IndexError):
            listing.remove_lines(-10)

        with self.assertRaises(IndexError):
            listing.remove_lines(100)

    def test_copy_lines(self):
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(4))

        result = listing.copy_lines(2, 2)
        self.assert_line_text('BC', result)

    def test_fold_lines(self):
        mock_hook, listing = self.hooked_listing()

        #---Typical usage, folding some lines
        listing.fold_lines(4, 6)

        self.assertEqual(5, len(listing.lines))
        self.assertEqual(10, listing.lines[0].line_number)
        self.assertEqual(11, listing.lines[1].line_number)
        self.assertEqual(12, listing.lines[2].line_number)
        self.assertEqual(16, listing.lines[4].line_number)

        self.assertTrue( isinstance(listing.lines[3], FoldedCodeLine) )

        # Verify hooks
        calls = [ 
            call(listing, 5),
            call(listing, 5),
        ]
        mock_hook.line_removed.assert_has_calls(calls)
        mock_hook.line_changed.assert_called_once()

        #---Fold testing different positions and parms

        # First line
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(4))

        listing.fold_lines(1, 2)
        self.assertEqual( FoldedCodeLine(2), listing.lines[0])
        self.assert_line_text('CD', listing.lines[1:])

        # One line
        listing = Listing(starting_line_number=10)
        listing.insert_lines(0, alpha_lines(4))

        listing.fold_lines(1, 1)
        self.assertEqual( FoldedCodeLine(1), listing.lines[0])
        self.assert_line_text('BCD', listing.lines[1:])

    def test_portion(self):
        # test finding a function
        code = Code(text=self.py_source)
        code.python_portion("foo")
        listing = Listing(code)
        expected = deepcopy(PY_CODE_LINES)[2:]
        self.assert_code_parts(expected, listing)

        # test find a function with an integer header
        code = Code(text=self.py_source)
        code.python_portion("foo", header=1)
        listing = Listing(code)
        expected = deepcopy(PY_CODE_LINES)[2:]
        expected.insert(0, PY_CODE_LINES[0])
        self.assert_code_parts(expected, listing)

        # test find a function with a tuple header
        code = Code(text=self.py_source)
        code.python_portion("foo", header=(1, 2))
        listing = Listing(code)
        expected = deepcopy(PY_CODE_LINES)[2:]
        expected.insert(0, PY_CODE_LINES[1])
        expected.insert(0, PY_CODE_LINES[0])
        self.assert_code_parts(expected, listing)
