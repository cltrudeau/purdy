"""
Colour Module (purdy.colour.py)
===============================

Contains classes to convert tokens to colour according to the various
supported renderers.
"""
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace, Punctuation

from purdy.parser import FoldedCodeLine, token_ancestor

# =============================================================================
# Plain Colourizer

class PlainColourizer:
    @classmethod
    def colourize(cls, code_line):
        """Returns the plain text version of the code line.

        :param code_line: a :class:`CodeLine` object to process
        """
        if isinstance(code_line, FoldedCodeLine):
            return '⋮'

        output = []
        if code_line.line_number != -1:
            output.append( cls.line_number(code_line.line_number) )

        output.extend([part.text for part in code_line.parts])
        return ''.join(output)

    @classmethod
    def line_number(cls, num):
        """Returns a colourized version of a line number"""
        return f'{num:3} '

# =============================================================================
# ANSI Colourizer

import colored

class ANSIColourizer:
    colours = {
        #                    fg256         attr
        Token:              ('',           '',),
        Whitespace:         ('',           '',),
        Comment:            ('cyan',       '',),
        Keyword:            ('yellow',     '',),
        Operator:           ('yellow',     '',),
        Name:               ('light_gray', '',),
        Name.Builtin:       ('#006688',    '',),
        Name.Function:      ('light_gray', '',),
        Name.Namespace:     ('light_gray', '',),
        Name.Class:         ('light_gray', '',),
        Name.Exception:     ('dark_green', '',),
        Name.Decorator:     ('#6666dd',    'bold',),
        Name.Variable:      ('',           '',),
        Name.Constant:      ('',           '',),
        Name.Attribute:     ('',           '',),
        Name.Tag:           ('',           '',),
        String:             ('magenta',    '',),
        Number:             ('magenta',    '',),
        Generic.Prompt:     ('dark_blue',  '',),
        Generic.Error:      ('dark_green', '',),
        Generic.Traceback:  ('#aa0000',    'bold',),
        Error:              ('#ff0000',    '',),
    }

    reset = colored.attr('reset')
    highlight = colored.bg('grey_23')
    get_code = lambda fn, colour: '' if not colour else fn(colour)

    @classmethod
    def colourize(cls, code_line):
        """Returns a text string with ANSI colour escapes corresponding to the
        tokens sent in

        :param code_line: a :class:`CodeLine` object to colourize
        """
        if isinstance(code_line, FoldedCodeLine):
            fg = colored.fg('white')
            bold = colored.attr('bold')
            return f'    {fg}{bold}⋮{cls.reset}'

        ancestor_list = cls.colours.keys()

        bg = ''
        if code_line.highlight:
            bg = cls.highlight

        output = []
        if code_line.line_number != -1:
            output.append( cls.line_number(code_line.line_number) )

        for part in code_line.parts:
            key = token_ancestor(part.token,   ancestor_list)
            colours = cls.colours[key]

            fg = cls.get_code(colored.fg, colours[0])
            attr = cls.get_code(colored.attr, colours[1])

            output.append(f'{fg}{attr}{bg}{part.text}{cls.reset}')

        return ''.join(output)

    @classmethod
    def line_number(cls, num):
        """Returns a colourized version of a line number"""
        fg = colored.fg('grey_39')
        return f'{fg}{num:3}{cls.reset} '

# =============================================================================
# HTML Colourizer

import html

class HTMLColourizer:
    colours = {
        Token:              '',
        Whitespace:         '',
        Comment:            'color: #8f5902; font-style: italic;',
        Keyword:            'color: #2048a7; font-weight: bold;',
        Operator:           'color: #ce5c00; font-weight: bold;',
        Name:               'color: #000000;',
        Name.Builtin:       'color: #3465a4;',
        Name.Function:      'color: #000000;',
        Name.Class:         'color: #000000;',
        Name.Exception:     'color: #cc0000; font-weight: bold;',
        Name.Decorator:     'color: #5c35cc; font-weight: bold;',
        Name.Variable:      '',
        Name.Constant:      '',
        Name.Attribute:     '',
        Name.Tag:           '',
        Punctuation:        'color: #000000; font-weight: bold;',
        String:             'color: #4e9a06;',
        String.Doc:         'color: #8f5902; font-style: italic;',
        Number:             'color: #0000cf; font-weight: bold;',
        Generic.Prompt:     'color: #8f5902;',
        Generic.Error:      'color: #ef2929;',
        Generic.Traceback:  'color: #a40000; font-weight: bold;',
    }

    highlight = 'background-color:#ddd; '

    @classmethod
    def colourize(cls, code_line):
        """Returns a text string with ANSI colour escapes corresponding to the
        tokens sent in

        :param code_line: a :class:`CodeLine` object to colourize
        """
        if isinstance(code_line, FoldedCodeLine):
            return '<span style="color: #000; font-weight: bold;">⋮</span>'

        ancestor_list = cls.colours.keys()

        output = []

        if code_line.line_number >= 0:
            output.append( HTMLColourizer.line_number(code_line.line_number) )
        
        if code_line.highlight:
            output.append(f'<span style="{cls.highlight}">')

        for part in code_line.parts:
            text = html.escape(part.text)
            key = token_ancestor(part.token,   ancestor_list)
            style = cls.colours[key]

            if style:
                output.append(f'<span style="{style}">{text}</span>')
            else:
                output.append(text)

        if code_line.highlight:
            output.append('</span>')

        return ''.join(output)

    @classmethod
    def line_number(cls, num):
        """Returns a colourized version of a line number"""
        style = ('color: #333; display: inline-block; min-width: 4ex;'
            'text-align: right; padding-right: 1ex;')
        return f'<span style="{style}">{num}</span>'

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
            output.append(chr(num))
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


class RTFColourizer:
    colours = {
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
        String.Doc:         '\\i \\cf2 %s\n \\i0', 
        Number:             '\\b \cf10 %s\n \\b0', 
        Generic.Prompt:     '\\cf2 %s\n',
        Generic.Error:      '\\cf11 %s\n',
        Generic.Traceback:  '\\b \cf12 %s\n\\b0\n', 
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
    def colourize(cls, code_line):
        """Returns a text string with RTF style tags. RTF uses a colour table,
        this styling assumes you're using the same colour table, available in
        the header in :attr:`RTFColourizer.rtf_header`.

        :param code_line: a :class:`CodeLine`   object to colourize
        """
        if isinstance(code_line, FoldedCodeLine):
            return '\\cf0 ⋮'

        ancestor_list = cls.colours.keys()

        output = []
        if code_line.line_number >= 0:
            output.append( RTFColourizer.line_number(code_line.line_number) )

        for part in code_line.parts:
            text = rtf_encode(part.text)
            key = token_ancestor(part.token,   ancestor_list)
            render = cls.colours[key] % text

            if code_line.highlight:
                render = cls.highlight % render

            output.append(render)

        return ''.join(output)

    @classmethod
    def line_number(cls, num):
        """Returns a colourized version of a line number"""
        return f'\\cf5 {num:3} \n'

# =============================================================================
# Urwid Colourizer

class UrwidColourizer:
    colours = {
        # urwid colour spec supports both 16 and 256 colour terminals
        #                    fg16            bg16    fg256   bg256
        Token:              ('',             '', '', '',             ''),
        Whitespace:         ('',             '', '', '',             ''),
        Comment:            ('dark cyan',    '', '', 'dark cyan',    ''),
        Keyword:            ('brown',        '', '', 'brown',        ''),
        Operator:           ('brown',        '', '', 'brown',        ''),
        Name:               ('light gray',   '', '', 'light gray',   ''),
        Name.Builtin:       ('dark cyan',    '', '', '#068',         ''),
        Name.Function:      ('dark cyan',    '', '', 'light gray',   ''),
        Name.Namespace:     ('dark cyan',    '', '', 'light gray',   ''),
        Name.Class:         ('dark cyan',    '', '', 'light gray',   ''),
        Name.Exception:     ('dark green',   '', '', 'dark green',   ''),
        Name.Decorator:     ('dark cyan',    '', '', '#66d,bold',    ''),
        Name.Variable:      ('',             '', '', '',             ''),
        Name.Constant:      ('',             '', '', '',             ''),
        Name.Attribute:     ('',             '', '', '',             ''),
        Name.Tag:           ('',             '', '', '',             ''),
        String:             ('dark magenta', '', '', 'dark magenta', ''),
        Number:             ('dark magenta', '', '', 'dark magenta', ''),
        Generic.Prompt:     ('dark blue',    '', '', 'dark blue',    ''),
        Generic.Error:      ('dark green',   '', '', 'dark green',   ''),
        Generic.Traceback:  ('',             '', '', '#a00,bold',    ''),
        Error:              ('dark green',   '', '', '#f00',         ''),
    }

    @classmethod
    def create_palette(cls):
        """Returns a list of colour tuples that Urwid uses as its palette. The
        list is based on the UrwidColourizer.colours with a couple extra items
        """
        palette = []
        for key, value in cls.colours.items():
            # for each item in our colours hash create a tuple consisting of
            # the token name and its values
            item = (str(key), ) + value
            palette.append( item )

            # do it again for highlighted tokens, for 16 colour mode change
            # both the fg and bg colour, for 256 colour mode just change the
            # background
            item = (str(key) + '_highlight', 'black', 'light gray', '', 
                value[3], 'g23')
            palette.append( item )

        # add miscellaneous other palette items
        palette.extend([
            ('folded', 'white', '', '', 'white', ''),
            ('line_number', 'dark gray', '', '', 'dark gray', ''),
            ('empty', '', '', '', '', ''),
            ('empty_highlight', '', 'light gray', '', '', 'g23'),
        ])
        
        return palette

    @classmethod
    def colourize_part(cls, code_part, highlight):
        ancestor_list = cls.colours.keys()
        key = str(token_ancestor(code_part.token, ancestor_list))
        if highlight:
            key += '_highlight'

        markup = (key, code_part.text)
        return markup

    @classmethod
    def colourize(cls, code_line):
        """Returns a list containing markup tuples as used by urwid.Text
        widgets.

        :param code_line: a :class:`CodeLine`   object to colourize
        """
        if isinstance(code_line, FoldedCodeLine):
            return ('folded', '     ⋮')

        ancestor_list = cls.colours.keys()

        output = []
        if code_line.line_number >= 0:
            output.append( UrwidColourizer.line_number(code_line.line_number) )

        for part in code_line.parts:
            key = str(token_ancestor(part.token, ancestor_list))
            if code_line.highlight:
                key += '_highlight'

            # Urwid uses a palette which has been built as a hash using the
            # names of the ancestor tokens as keys and the fg/bg colour
            # choices as values, each piece of marked up text is a tuple of
            # the palette key and the text to display
            markup = (key, part.text)
            output.append(markup)

        return output

    @classmethod
    def line_number(cls, num):
        """Returns a colourized version of a line number"""
        return ('line_number', f'{num:3} ')

# =============================================================================

COLOURIZERS = {
    'plain':PlainColourizer,
    'ansi':ANSIColourizer,
    'html':HTMLColourizer,
    'rtf':RTFColourizer,
    'urwid':UrwidColourizer,
}
