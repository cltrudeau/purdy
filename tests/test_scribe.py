from pathlib import Path

from waelstow import capture_stdout

from purdy.content import Code, Listing
from purdy.scribe import (range_set_to_list, print_tokens, print_ansi,
    print_html, print_rtf)

from tests.base import PurdyContentTest

# =============================================================================

class TestScribe(PurdyContentTest):
    def test_range_set_to_list(self):
        expected = [3,]
        result = range_set_to_list('3')
        self.assertEqual(expected, result)

        expected = [3, 4, 5]
        result = range_set_to_list('3-5')
        self.assertEqual(expected, result)

        expected = [3, 4, 5, 6, 7, 8, 9]
        result = range_set_to_list('3-5,9,4,5-8')
        self.assertEqual(expected, result)

    def file_compare(self, datafile, fn, *args):
        with capture_stdout() as captured:
            fn(*args)

            filename = Path(__file__).parent / f'data/{datafile}'
            with open(filename.resolve()) as f:
                expected = f.read()
                self.assertEqual(expected, captured.getvalue())

    def test_tokens(self):
        code = Code(text=self.py_source, lexer_name='py3')
        listing = Listing(code)

        self.file_compare('print_tokens_ansi.out', print_tokens, listing, True)
        self.file_compare('print_tokens_bw.out', print_tokens, listing, False)

    def test_ansi(self):
        code = Code(text=self.py_source, lexer_name='py3')
        listing = Listing(code)
        listing.set_display('ansi')
        self.file_compare('print_ansi.out', print_ansi, listing)

    def test_html(self):
        code = Code(text=self.py_source, lexer_name='py3')
        listing = Listing(code)
        listing.set_display('html')
        self.file_compare('print_html_snippet.out', print_html, listing, True)
        self.file_compare('print_html_full.out', print_html, listing, False)

    def test_rtf(self):
        code = Code(text=self.py_source, lexer_name='py3')
        listing = Listing(code)
        listing.set_display('rtf')
        self.file_compare('print_rtf_nobg.out', print_rtf, listing)
        self.file_compare('print_rtf_bg.out', print_rtf, listing, 'ccc')

# commented out for pyflakes
#    def __test_generate(self):
#        ### This stub code is used to generate data files to compare against
#        code = Code(text=self.py_source, lexer_name='py3')
#        listing = Listing(code)
#        listing.set_display('rtf')
#
#        with capture_stdout() as captured:
#            print_rtf(listing, 'ccc')
#
#            with open('print_rtf_bg.out', 'w') as f:
#                f.write(captured.getvalue())
