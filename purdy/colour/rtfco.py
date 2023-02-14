from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace, Punctuation, Text, Literal

from purdy.parser import FoldedCodeLine, token_ancestor

# =============================================================================
# RTF Colourizer

import struct

def rtf_encode(text):
    """RTF uses a weird UTF-16 decimal escape sequence for encoding unicode.
    This method take a string and returns an RTF encoded version of it."""
    output = []
    data = text.encode('utf-16le')
    length = len(data) // 2

    # use struct.unpack to turn the pairs of bytes into decimal unicode escape
    # numbers
    parts = struct.unpack(f'<{length}H', data)
    index = 0
    size = len(parts)

    while index < size:
        num = parts[index]

        if num <= 127:
            # regular ascii
            letter = chr(num)

            # Escape characters that are used by RTF 
            if letter == '\\':
                output.append('\\\\')
            elif letter in '{}':
                output.append('\\' + letter)
            else:
                output.append(letter)
        elif num <= 256:
            # extended ascii, use hex notation
            output.append(f"\\'{num:2x}" )
        elif num < 55296:
            # 0xD800 (55296) is the the boundary for two-word encoding, less
            # than this means it is a single item
            output.append(f"\\uc0\\u{num}")
        else:
            # greater than 0xD800, means two words
            index += 1
            next_num = parts[index]
            output.append(f"\\uc0\\u{num} \\u{next_num}")

        index += 1

    return ''.join(output)

# -----------------------------------------------------------------------------

class RTFHeaders:
    preamble = r"""{\rtf1\ansi\ansicpg1252
{\fonttbl\f0\fnil\fcharset0 RobotoMono-Regular;}
"""
    color_table = r"""
{\colortbl;\red255\green255\blue255;\red143\green89\blue2;\red32\green72\blue167;\red206\green92\blue0;
\red0\green0\blue0;\red52\green101\blue164;\red204\green0\blue0;\red92\green53\blue204;\red78\green154\blue6;
\red0\green0\blue207;\red239\green41\blue41;\red164\green0\blue0;
\red213\green213\blue213;}
"""

    color_table_background_template = r"""
{\colortbl;\red255\green255\blue255;\red143\green89\blue2;\red32\green72\blue167;\red206\green92\blue0;
\red0\green0\blue0;\red52\green101\blue164;\red204\green0\blue0;\red92\green53\blue204;\red78\green154\blue6;
\red0\green0\blue207;\red239\green41\blue41;\red164\green0\blue0;
\red213\green213\blue213;%s}
"""

    font_spec = r'\f0\fs28' + '\n'

# -----------------------------------------------------------------------------

_code_palette = {
    Token:              '\\cf0 %s\n',
    Whitespace:         '\\cf0 %s\n',
    Comment:            '\\i \\cf2 %s\n\\i0\n',
    Keyword:            '\\b \\cf3 %s\n\\b0\n',
    Operator:           '\\b \\cf4 %s\n\\b0\n', 
    Name:               '\\cf5 %s\n',
    Name.Builtin:       '\\cf6 %s\n', 
    Name.Function:      '\\cf5 %s\n',
    Name.Class:         '\\cf5 %s\n',
    Name.Exception:     '\\b \\cf7 %s\n\\b0\n', 
    Name.Decorator:     '\\b \\cf8 %s\n\\b0\n', 
    Name.Variable:      '\\cf0 %s\n',
    Name.Constant:      '\\cf0 %s\n',
    Name.Attribute:     '\\cf0 %s\n',
    Name.Tag:           '\\cf0 %s\n',
    Punctuation:        '\\b \\cf5 %s\n\\b0\n', 
    String:             '\\cf9 %s\n', 
    String.Doc:         '\\i \\cf2 %s\n\\i0', 
    Number:             '\\b \cf10 %s\n\\b0', 
    Generic.Prompt:     '\\cf2 %s\n',
    Generic.Error:      '\\cf11 %s\n',
    Generic.Traceback:  '\\b \cf12 %s\n\\b0\n', 
    Error:              '\\cf11 %s\n',
}

_xml_palette = dict(_code_palette)
_xml_palette.update({
    Name.Attribute: '\\b \\cf3 %s\n\\b0\n',
    Name.Tag:       '\\cf6 %s\n', 
    Keyword:        '\\cf6 %s\n', 
    Punctuation:    '\\cf6 %s\n', 
})

_doc_palette = dict(_xml_palette)
_doc_palette.update({
    Generic.Emph:   '\\cf11 %s\n',
    Generic.Strong: '\\b \cf12 %s\n\\b0\n', 
    Literal:        '\\cf0 %s\n',
    Generic.Heading:'\\cf2 %s\n',
    Generic.Subheading:'\\cf2 %s\n',
})

class RTFColourizer:
    palettes = {
        'code':_code_palette,
        'xml':_xml_palette,
        'doc':_doc_palette,
    }

    rtf_header = RTFHeaders.preamble + RTFHeaders.color_table + \
        RTFHeaders.font_spec

    highlight = '\\cb13 %s \\cb1'

    @classmethod
    def set_background_colour(cls, colour):
        """RTF doesn't really support turning background colours off, once you
        have a background colour it can only set the whole doc to something
        else. This makes highlighting weird if your background colour isn't
        white. Calling this method updates the colour table with the specified
        value and changes the document to have that background colour

        :param colour: string containing a HTML hex colour code without the
                       starting #, e.g. "ccc", "f3b2e1"
        """
        double_it = lambda s, i: f'0x{s[i]}{s[i]}'

        # calculate the integer value of the hex colour
        if len(colour) == 3:
            red = int(double_it(colour, 0), base=16)
            green = int(double_it(colour, 1), base=16)
            blue = int(double_it(colour, 2), base=16)
        else:
            red = int(f'0x{colour[0:2]}', base=16)
            green = int(f'0x{colour[2:4]}', base=16)
            blue = int(f'0x{colour[4:6]}', base=16)

        bg = f'\\red{red}\\green{green}\\blue{blue};'  # rtf colour descriptor

        # update the header to include the new background colour and the
        # highlight spec to use it
        cls.rtf_header = RTFHeaders.preamble + \
            RTFHeaders.color_table_background_template % bg + \
            RTFHeaders.font_spec + '\\cb14 \n'
        cls.highlight = '\\cb13 %s \\cb14'

    @classmethod
    def reset_background_colour(cls):
        """When testing, need to put the class back in its original state."""
        cls.rtf_header = RTFHeaders.preamble + RTFHeaders.color_table + \
            RTFHeaders.font_spec

    @classmethod
    def colourize(cls, code_line):
        """Returns a text string with RTF style tags. RTF uses a colour table,
        this styling assumes you're using the same colour table, available in
        the header in :attr:`RTFColourizer.rtf_header`.

        :param code_line: a :class:`CodeLine`   object to colourize
        """
        if isinstance(code_line, FoldedCodeLine):
            return '\\cf0 ⋮'

        palette = code_line.lexer.palette
        ancestor_list = cls.palettes[palette].keys()

        output = []
        if code_line.line_number >= 0:
            output.append( cls.line_number(code_line.line_number) )

        for part in code_line.parts:
            text = rtf_encode(part.text)
            key = token_ancestor(part.token,   ancestor_list)
            render = cls.palettes[palette][key] % text

            if code_line.highlight:
                render = cls.highlight % render

            output.append(render)

        return ''.join(output)

    @classmethod
    def line_number(cls, num):
        """Returns a colourized version of a line number"""
        return f'\\cf5 {num:3} \n'
