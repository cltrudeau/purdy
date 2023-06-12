from pathlib import Path

from pygments.token import Generic

from tests.base import PurdyCase

from purdy.content import Code, Listing, _ListingLine
from purdy.filters import remove_lines, remove_double_blanks
from purdy.parser import (Parser, CodeLine, CodePart, LineNumber, HighlightOn,
    HighlightOff)
from purdy.lexers import NewlineLexer

# =============================================================================

class CodeObjectTest(PurdyCase):
    def test_detection(self):
        # Filename is a Path object
        path = Path(__file__).resolve().parent / Path("data/cats.py")
        code = Code(path)
        self.assertEqual('py', code.parser.spec.name)

        # Filename is a string
        filename = str(path)
        code = Code(filename)
        self.assertEqual('py', code.parser.spec.name)

    def test_bad_detect(self):
        # Running detect without a filename
        with self.assertRaises(AttributeError):
            Code(text="foo")

        # Non-existant parser
        with self.assertRaises(AttributeError):
            Code(text="foo", parser="herekittykitty")

        # Running detect on a weird file
        path = Path(__file__).resolve().parent / Path("data/weird.weird")
        with self.assertRaises(AttributeError):
            Code(path)

    def test_custom_parser(self):
        parser = Parser.custom('custom', 'Testing Custom', NewlineLexer, False,
            'doc')

        Code(text="Some text\nAnd more", parser=parser)

    def test_filter_chains(self):
        source = (
            "She walks in beauty\n"
            "like the night,\n\n"
            "Of cloudless climes\n\n"
            "and starry skies;\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;"
        )

        code = Code(
            text=source,
            parser='plain',
            filters=[remove_double_blanks, remove_lines(1, (3, 2))]
        )

        expected = (
            "like the night,\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;"
        )

        self.assertEqual(expected, code.source)

    def test_clone(self):
        # Create some source running some filters
        source = (
            "She walks in beauty\n"
            "like the night,\n\n"
            "Of cloudless climes\n\n"
            "and starry skies;\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;"
        )

        code = Code(
            text=source,
            parser='plain',
            filters=[remove_double_blanks, remove_lines(1, (3, 2))]
        )

        # Clone it and run another filter (newline is stripped from source)
        expected = (
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;"
        )
        clone = code.clone(filters=[remove_lines(1)])
        self.assertEqual(expected, clone.source)

    def test_line_access(self):
        source = (
            "She walks in beauty\n"
            "like the night,\n"
            "Of cloudless climes\n"
            "and starry skies;\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;"
        )

        original = Code(text=source, parser='plain')
        code = original.clone()

        # Looping
        for num, line in enumerate(code):
            self.assertEqual(original.lines[num], line)

        # Slicing
        self.assertEqual(original.lines[1], code[1])
        self.assertEqual(original.lines[1:3], list(code[1:3]))

        # Chunking
        self.assertEqual(original.lines[0:2], list(code.chunk(2)))
        self.assertEqual(original.lines[2:4], list(code.chunk(2)))
        self.assertEqual(original.lines[4:6], list(code.chunk(2)))

        # Chunking past the boundary
        code.current_line = 0
        self.assertEqual(original.lines, list(code.chunk(8)))


class ListingTest(PurdyCase):
    def test_access(self):
        source = (
            "She walks in beauty\n"
            "like the night,\n"
            "Of cloudless climes\n"
            "and starry skies;\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;"
        )

        code = Code(text=source, parser='plain')
        listing = Listing(code)

        # Slicing
        self.assertEqual(code.lines[1], listing[1])
        self.assertEqual(code.lines[1:3], list(listing[1:3]))

    # -----
    # Line Numbers
    def test_line_numbers(self):

        # Build a string with A through O on a line each
        source = "\n".join([chr(num) for num in range(65, 80)])

        code = Code(text=source, parser='plain')
        listing = Listing(code)

        for num, line in enumerate(listing.lines):
            expected = CodeLine(code.parser.spec, [CodePart(Generic.Output,
                f"{chr(num+65)}")])

            self.assertEqual(expected, line)

        # Turn on line numbers
        listing.starting_line_number = 10

        for num, line in enumerate(listing.lines):
            parts = [
                CodePart(LineNumber, f"{num + 10:2} "),
                CodePart(Generic.Output, f"{chr(num+65)}"),
            ]
            expected = CodeLine(code.parser.spec, parts)

            self.assertEqual(expected, line)

        # Turn them back off
        listing.starting_line_number = None

        for num, line in enumerate(listing.lines):
            expected = CodeLine(code.parser.spec, [CodePart(Generic.Output,
                f"{chr(num+65)}")])

            self.assertEqual(expected, line)

    def test_line_number_toggle(self):
        source = (
            "She walks in beauty\n"
            "like the night,\n"
            "Of cloudless climes\n"
            "and starry skies;\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;"
        )

        code = Code(text=source, parser='plain')
        listing = Listing(code)

        # Toggle line numbers on (defaults to 1)
        listing.toggle_line_numbers()

        self.assertEqual(LineNumber, listing.lines[0].parts[0].token)
        self.assertEqual('1 ', listing.lines[0].parts[0].text)

        # Toggle them off
        listing.toggle_line_numbers()
        self.assertNotEqual(LineNumber, listing.lines[0].parts[0].token)

        # Try again with assigned numbers (this turns them on)
        listing.starting_line_number = 10

        # Toggle them off
        listing.toggle_line_numbers()
        self.assertNotEqual(LineNumber, listing.lines[0].parts[0].token)

        # Toggle them back on and make sure they're still starting at 10
        listing.toggle_line_numbers()

        self.assertEqual(LineNumber, listing.lines[0].parts[0].token)
        self.assertEqual('10 ', listing.lines[0].parts[0].text)

    # -----
    # Highlight
    def assert_highlight_count(self, lines, expected_count):
        on_count = 0
        off_count = 0
        for line in lines:
            for part in line.parts:
                if part.token == HighlightOn:
                    on_count += 1
                if part.token == HighlightOff:
                    off_count += 1

        self.assertEqual(expected_count, on_count)
        self.assertEqual(expected_count, off_count)

    def test_highlight_line(self):
        source = (
            "She walks in beauty\n"
            "like the night,\n"
            "Of cloudless climes"
        )

        code = Code(text=source, parser='plain')
        listing = Listing(code)
        listing.highlight(1, 3)

        # Validate highlight markers
        self.assertEqual(HighlightOn, listing.lines[0].parts[0].token)
        self.assertEqual(HighlightOff, listing.lines[0].parts[-1].token)
        self.assertEqual(HighlightOn, listing.lines[2].parts[0].token)
        self.assertEqual(HighlightOff, listing.lines[2].parts[-1].token)

        self.assert_highlight_count(listing.lines, 2)

        # Turn them all off
        listing.highlight_off(1)
        listing.highlight_off(3)
        self.assert_highlight_count(listing.lines, 0)

        # Do it again with line numbers on
        listing.starting_line_number = 1
        listing.highlight(1, 3)

        # Validate highlight markers (now in the second position)
        self.assertEqual(HighlightOn, listing.lines[0].parts[1].token)
        self.assertEqual(HighlightOff, listing.lines[0].parts[-1].token)
        self.assertEqual(HighlightOn, listing.lines[2].parts[1].token)
        self.assertEqual(HighlightOff, listing.lines[2].parts[-1].token)

        self.assert_highlight_count(listing.lines, 2)

        # Turn them all off
        listing.highlight_off(1)
        listing.highlight_off(3)
        self.assert_highlight_count(listing.lines, 0)
        listing.starting_line_number = None

        # Do it again with a range
        listing.highlight(1, (2, 3) )

        # Validate highlight markers
        self.assertEqual(HighlightOn, listing.lines[0].parts[0].token)
        self.assertEqual(HighlightOff, listing.lines[0].parts[-1].token)
        self.assertEqual(HighlightOn, listing.lines[1].parts[0].token)
        self.assertEqual(HighlightOff, listing.lines[1].parts[-1].token)
        self.assertEqual(HighlightOn, listing.lines[2].parts[0].token)
        self.assertEqual(HighlightOff, listing.lines[2].parts[-1].token)

        self.assert_highlight_count(listing.lines, 3)
        listing.highlight_off((1, 3))

        # Do it again with text arguments
        listing.highlight('1', '2-3')

        # Validate highlight markers
        self.assertEqual(HighlightOn, listing.lines[0].parts[0].token)
        self.assertEqual(HighlightOff, listing.lines[0].parts[-1].token)
        self.assertEqual(HighlightOn, listing.lines[1].parts[0].token)
        self.assertEqual(HighlightOff, listing.lines[1].parts[-1].token)
        self.assertEqual(HighlightOn, listing.lines[2].parts[0].token)
        self.assertEqual(HighlightOff, listing.lines[2].parts[-1].token)

        self.assert_highlight_count(listing.lines, 3)

    def test_highlight_fractional(self):
        # Highlighting from bar to bar
        #                   |     |
        source = """print("foo", bar)"""

        code = Code(text=source, parser='py')
        listing = Listing(code)
        listing.highlight('1.9-15')

        # Validate the line got highlighted and the sentence got split
        # in the right place
        self.assertEqual(HighlightOn, listing.lines[0].parts[4].token)
        self.assertEqual(HighlightOff, listing.lines[0].parts[9].token)

        self.assert_highlight_count(listing.lines, 1)

        # Make sure it didn't bugger the content up
        text = ''.join([part.text for part in listing.lines[0].parts])
        self.assertEqual(source, text)

    def test_highlight_negative(self):
        source = (
            "She walks in beauty\n"
            "like the night,\n"
            "Of cloudless climes"
        )

        code = Code(text=source, parser='plain')
        listing = Listing(code)
        listing.highlight(-1)

        # Validate highlight markers
        self.assertEqual(HighlightOn, listing.lines[-1].parts[0].token)

        # Now turn it off
        listing.highlight_off(-1)
        self.assert_highlight_count(listing, 0)

        # Do it again with a string
        listing.highlight('-1')

        # Validate highlight markers
        self.assertEqual(HighlightOn, listing.lines[-1].parts[0].token)

        # Now turn it off
        listing.highlight_off(-1)
        self.assert_highlight_count(listing, 0)

        # Try again with fractional
        listing.highlight('-1.1-3')
        self.assertEqual(HighlightOn, listing.lines[-1].parts[0].token)

    def test_highlight_bad(self):
        listing = Listing()
        with self.assertRaises(ValueError):
            listing.highlight( (-1, 3) )

        with self.assertRaises(ValueError):
            listing.highlight( '-1-3' )

    def test_highlight_fractional_line_numbers(self):
        # Highlighting from bar to bar
        #                   |     |
        source = """print("foo", bar)"""

        code = Code(text=source, parser='py')
        listing = Listing(code)
        listing.starting_line_number = 1
        listing.highlight('1.9-15')

        # Validate the line got highlighted and the sentence got split
        # in the right place (one more than other test because of line #s)
        self.assertEqual(HighlightOn, listing.lines[0].parts[5].token)
        self.assertEqual(HighlightOff, listing.lines[0].parts[10].token)

        self.assert_highlight_count(listing.lines, 1)

        # Make sure it didn't bugger the content up
        text = ''.join([part.text for part in listing.lines[0].parts])
        self.assertEqual("1 " + source, text)

    def test_highlight_off_all(self):
        source = (
            "She walks in beauty\n"
            "like the night,\n"
            "Of cloudless climes\n"
            "and starry skies;\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;"
        )

        code = Code(text=source, parser='plain')
        listing = Listing(code)
        listing.starting_line_number = 1
        listing.highlight(1, (3, 4), '6.1-4')
        listing.highlight_off_all()

        for line in listing.lines:
            for part in line.parts:
                self.assertNotEqual(HighlightOn, part.token)
                self.assertNotEqual(HighlightOff, part.token)

    # -----
    # Segmenting
    def test_wrap_at_length(self):
        # Test without a split
        source = "She walks in beauty"
        code = Code(text=source, parser='plain')
        listing = Listing(code)
        pieces = listing.lines[0].wrap_at_length(80)

        # Should not have done anything
        token = listing.lines[0].parts[0].token
        self.assertEqual(1, len(pieces))
        self.assertEqual(token, pieces[0][0].token)
        self.assertEqual(source, pieces[0][0].text)

        # ---
        # Test with a single split
        left = "She walks in beauty "
        right = "like the night"
        source = left + right

        code = Code(text=source, parser='plain')
        listing = Listing(code)
        pieces = listing.lines[0].wrap_at_length(len(left))

        # Should not have done anything
        self.assertEqual(2, len(pieces))
        self.assertEqual(token, pieces[0][0].token)
        self.assertEqual(left, pieces[0][0].text)
        self.assertEqual(token, pieces[1][0].token)
        self.assertEqual(right, pieces[1][0].text)

        # ---
        # Test with a double split
        left  = "She walks in beauty "
        mid   = "like the night Of cl"
        right = "less climes"
        source = left + mid + right

        code = Code(text=source, parser='plain')
        listing = Listing(code)
        pieces = listing.lines[0].wrap_at_length(len(left))

        # Should not have done anything
        self.assertEqual(3, len(pieces))
        self.assertEqual(token, pieces[0][0].token)
        self.assertEqual(left, pieces[0][0].text)
        self.assertEqual(token, pieces[1][0].token)
        self.assertEqual(mid, pieces[1][0].text)
        self.assertEqual(token, pieces[2][0].token)
        self.assertEqual(right, pieces[2][0].text)

    # -----
    # Operations
#    def test_append(self):
#        source1 = (
#            "She walks in beauty\n"
#            "like the night,\n"
#            "Of cloudless climes\n"
#        )
#
#        source2 = (
#            "and starry skies;\n"
#            "And all that's best of dark and bright\n"
#            "Meet in her aspect and her eyes;"
#        )
#
#        code1 = Code(text=source1, parser='plain')
#        code2 = Code(text=source2, parser='plain')
#
#        listing = Listing(code1)
#        listing.starting_line_number = 1
#        listing.append(code2)
#        nantucket = "There once was a man from Nantucket"
#        listing.append(nantucket)
#
#        bucket = "Who couldn't find his bucket"
#        code_line = CodeLine(Parser.registry['plain'], [
#            CodePart(Generic.Output, bucket)])
#        listing.append(code_line)
#
#        self.assertEqual(8, len(listing.lines))
#        self.assertEqual('1 ', listing.lines[0].parts[0].text)
#        self.assertEqual('8 ', listing.lines[7].parts[0].text)
#
#        expected = source2.split("\n")[2]
#        self.assertEqual(expected, listing.lines[5].parts[1].text)
#
#        self.assertEqual(nantucket, listing.lines[6].parts[1].text)
#        self.assertEqual(bucket, listing.lines[7].parts[1].text)
#
#    def test_append_bad(self):
#        listing = Listing()
#        with self.assertRaises(ValueError):
#            listing.append(3)
