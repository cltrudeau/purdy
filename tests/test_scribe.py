import sys
from pathlib import Path

from waelstow import capture_stdout

from purdy.content import Code, Listing
from purdy.colour import COLOURIZERS

from purdy.scribe import (range_set_to_list, print_tokens, print_ansi,
    print_html, print_rtf)

from tests.base import PurdyContentTest

RTFColourizer = COLOURIZERS['rtf']

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
        self.maxDiff = None

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
        RTFColourizer.reset_background_colour()
        code = Code(text=self.py_source, lexer_name='py3')
        listing = Listing(code)
        listing.set_display('rtf')
        self.file_compare('print_rtf_nobg.out', print_rtf, listing)
        self.file_compare('print_rtf_bg.out', print_rtf, listing, 'ccc')

# Uncomment to regenerate a data file
#    def test_generate(self):
#        print('*** Generating data files')
#
#        ### This stub code is used to generate data files to compare against
#        code = Code(text=self.py_source, lexer_name='py3')
#        listing = Listing(code)
#
#        config = {
#            #'print_tokens_ansi.out':[
#            #    None,
#            #    print_tokens, 
#            #    [True, ],
#            #],
#            #'print_tokens_bw.out':[
#            #    None,
#            #    print_tokens, 
#            #    [False, ],
#            #],
#            #'print_ansi.out':[
#            #    'ansi',
#            #    print_ansi, 
#            #    [],
#            #],
#            #'print_rtf_nobg.out':[
#            #    'rtf',
#            #    print_rtf, 
#            #    [],
#            #],
#            #'print_rtf_bg.out':[
#            #    'rtf',
#            #    print_rtf, 
#            #    ['ccc', ],
#            #],
#            #'print_html_snippet.out':[
#            #    'html',
#            #    print_html, 
#            #    [True],
#            #],
#            #'print_html_full.out':[
#            #    'html',
#            #    print_html, 
#            #    [False],
#            #],
#        }
#
#        for filename, parms in config.items():
#            print('    => generating', filename)
#            with capture_stdout() as captured:
#                if parms[0]:
#                    listing.set_display(parms[0])
#
#                fn = parms[1]
#                fn(listing, *parms[2])
#
#                with open(filename, 'w') as f:
#                    f.write(captured.getvalue())
