from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace, Punctuation

from .base import BaseColourizer
from purdy.parser import FoldedCodeLine, token_ancestor

# =============================================================================
# ANSI Colourizer: augments code with colour specified using ANSI terminal 
#                  escape sequences

import colored

class ANSIColourizer(BaseColourizer):
    palettes = {
        'code':{
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
    }

    reset = colored.attr('reset')
    highlight = colored.bg('grey_23')
    get_code = lambda self, fn, colour: '' if not colour else fn(colour)

    def __init__(self, palette):
        self.palette = palette

    def colourize(self, code_line):
        """Returns a text string with ANSI colour escapes corresponding to the
        tokens sent in

        :param code_line: a :class:`CodeLine` object to colourize
        """
        if isinstance(code_line, FoldedCodeLine):
            fg = colored.fg('white')
            bold = colored.attr('bold')
            return f'    {fg}{bold}⋮{self.reset}'

        ancestor_list = self.palettes[self.palette].keys()

        bg = ''
        if code_line.highlight:
            bg = self.highlight

        output = []
        if code_line.line_number != -1:
            output.append( self.line_number(code_line.line_number) )

        for part in code_line.parts:
            key = token_ancestor(part.token, ancestor_list)
            colours = self.palettes[self.palette][key]

            fg = self.get_code(colored.fg, colours[0])
            attr = self.get_code(colored.attr, colours[1])

            output.append(f'{fg}{attr}{bg}{part.text}{self.reset}')

        return ''.join(output)

    def line_number(self, num):
        """Returns a colourized version of a line number"""
        fg = colored.fg('grey_39')
        return f'{fg}{num:3}{self.reset} '
