from unittest import TestCase

from purdy.content import Code, Listing
from purdy.export.text import (listing_to_text, listing_to_tokens,
    listing_to_tokens_outline)
from purdy.export.html import listing_to_html
from purdy.export.rtf import listing_to_rtf

# =============================================================================

class TextExportTest(TestCase):
    def test_listing_to_text(self):
        source = (
            "def is_armstrong_number(num):\n"
            "    # Armstrong if: ABC == A^3 + B^3 + C^3\n"
            "    # nth power of the digits summed is equal to the number\n"
            "    total = 0\n"
            "    length = len(str(num))\n"
            "\n"
            "    temp = num\n"
            "    while temp > 0:\n"
            "        digit = temp % 10\n"
            "        total += digit ** length\n"
            "        temp //= 10\n"
            "\n"
            "    if num == total:\n"
            "        return True\n"
            "\n"
            "    return False\n"
        )

        code = Code(text=source, parser="py")
        listing = Listing(code=code)

        result = listing_to_text(listing)
        self.assertEqual(source, result)

        # Do it again, this time with line numbers (need to remove the newline
        # at the end to get the output to match)
        lines = source[:-1].split("\n")
        output = []
        for num, line in enumerate(lines):
            output.append( f"{num + 1:2} {line}" )

        expected = "\n".join(output) + "\n"

        listing.starting_line_number = 1

        result = listing_to_text(listing)
        self.assertEqual(expected, result)

    def test_listing_to_tokens(self):
        source = (
            "def add(a, b):\n"
            "    return a + b"
        )

        code = Code(text=source, parser='py')
        listing = Listing(code)

        expected = (
            "(Token.Keyword)def(Token.Text) (Token.Name.Function)add"
            "(Token.Punctuation)((Token.Name)a(Token.Punctuation),"
            "(Token.Text) (Token.Name)b(Token.Punctuation))"
            "(Token.Punctuation):\n"
            "(Token.Text)    (Token.Keyword)return(Token.Text) "
            "(Token.Name)a(Token.Text) (Token.Operator)+"
            "(Token.Text) (Token.Name)b\n"
        )

        result = listing_to_tokens(listing)
        self.assertEqual(expected, result)

    def test_listing_to_tokens_outline(self):
        source = (
            "def add(a, b):\n"
            "    return a + b"
        )

        code = Code(text=source, parser='py')
        listing = Listing(code)

        expected = (
            "Lexer: 'py' Python 3 Source\n"
            "      (Token.Keyword) def\n"
            "         (Token.Text)  \n"
            "(Token.Name.Function) add\n"
            "  (Token.Punctuation) (\n"
            "         (Token.Name) a\n"
            "  (Token.Punctuation) ,\n"
            "         (Token.Text)  \n"
            "         (Token.Name) b\n"
            "  (Token.Punctuation) )\n"
            "  (Token.Punctuation) :\n"
            "[EOL]\n"
            "         (Token.Text)     \n"
            "      (Token.Keyword) return\n"
            "         (Token.Text)  \n"
            "         (Token.Name) a\n"
            "         (Token.Text)  \n"
            "     (Token.Operator) +\n"
            "         (Token.Text)  \n"
            "         (Token.Name) b\n"
            "[EOL]\n"
        )

        result = listing_to_tokens_outline(listing)
        self.assertEqual(expected, result)

    def test_listing_to_html(self):
        # Shitty test that copy/pastes the output, but at least checks if the
        # conversion runs
        source = 'print("hello there", value)'
        code = Code(text=source, parser='py')
        listing = Listing(code)

        expected = (
            '  <div style="background :#f8f8f8; overflow:auto; width:auto; border:solid gray; border-width:.1em .1em .1em .8em; padding:.2em .6em;">\n'
            '    <pre style="margin: 0; line-height:125%">\n'
            '<span style="color: #3465a4;">print</span><span style="color: #000000; font-weight: bold;">(</span><span style="color: #4e9a06;">"</span><span style="color: #4e9a06;">hello there</span><span style="color: #4e9a06;">"</span><span style="color: #000000; font-weight: bold;">,</span><span style=""> </span><span style="color: #000000;">value</span><span style="color: #000000; font-weight: bold;">)</span>\n'
            '    </pre>\n'
            '  </div>\n'
        )

        result = listing_to_html(listing, True)
        self.assertEqual(expected, result)

        # Do it again with a full document
        prefix = (
            '<!doctype html>\n'
            '<html lang="en">\n'
            '<body>\n'
        )
        suffix = (
            '</body>\n'
            '</html>\n'
        )

        expected = prefix + expected + suffix
        result = listing_to_html(listing, False)
        self.assertEqual(expected, result)

    def test_listing_to_rtf(self):
        # Another shitty test that copy/pastes the output, but at least checks
        # if the conversion runs
        source = 'print("hello there", value)'
        code = Code(text=source, parser='py')
        listing = Listing(code)


        header = (
            r'{\rtf1\ansi\ansicpg1252' + "\n"
            r'{\fonttbl\f0\fnil\fcharset0 RobotoMono-Regular;}' + "\n"
        )

        table = r'{\colortbl;\red255\green255\blue255;\red143\green89\blue2;\red32\green72\blue167;\red206\green92\blue0;\red0\green0\blue0;\red52\green101\blue164;\red204\green0\blue0;\red92\green53\blue204;\red78\green154\blue6;\red0\green0\blue207;\red239\green41\blue41;\red164\green0\blue0;\red213\green213\blue213;%s}\f0\fs28' + "\n"

        body = (
            r'%s\cf6 print' + "\n"
            r'\b \cf5 (' + "\n"
            r'\b0' + "\n"
            r'\cf9 "' + "\n"
            r'\cf9 hello there' + "\n"
            r'\cf9 "' + "\n"
            r'\b \cf5 ,' + "\n"
            r'\b0' + "\n"
            r'\cf0  ' + "\n"
            r'\cf5 value' + "\n"
            r'\b \cf5 )' + "\n"
            r'\b0' + "\n"
            '\\' + "\n"
            r'}'
        )

        expected = header + table % '' + body % r'\cb1 '
        result = listing_to_rtf(listing)
        self.assertEqual(expected, result)

        # Do it again with a background colour
        expected = header + table % r'\red255\green0\blue0;' + r'\cb14' + \
            "\n" + body % ''
        result = listing_to_rtf(listing, 'f00')
        self.assertEqual(expected, result)
