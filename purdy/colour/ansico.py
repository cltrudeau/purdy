from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace, Punctuation, Text, Literal

from purdy.parser import FoldedCodeLine, token_ancestor

# =============================================================================
# ANSI Colourizer: augments code with colour specified using ANSI terminal 
#                  escape sequences

_code_palette = {
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

_xml_palette = dict(_code_palette)
_xml_palette.update({
    Name.Attribute: ('yellow',     '',),
    Keyword:        ('#006688',    '',),
    Name.Tag:       ('#006688',    '',),
    Punctuation:    ('#006688',    '',),
})

_doc_palette = dict(_code_palette)
_doc_palette.update({
    Text:           ('light_gray', '',),
    Name.Tag:       ('#006688',    '',),
    Name.Attribute: ('#006688',    '',),
    Punctuation:    ('#006688',    '',),
    Generic.Heading:('yellow',     '',),
    Generic.Subheading:('yellow',     '',),
    Literal:        ('magenta',    '',),
    Generic.Emph:   ('dark_blue',   '',),
    Generic.Strong: ('dark_green',   'bold',),
})

import colored

class ANSIColourizer:
    palettes = {
        'code':_code_palette,
        'xml':_xml_palette,
        'doc':_doc_palette,
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

        palette = code_line.lexer.palette
        ancestor_list = cls.palettes[palette].keys()

        bg = ''
        if code_line.highlight:
            bg = cls.highlight

        output = []
        if code_line.line_number != -1:
            output.append( cls.line_number(code_line.line_number) )

        for part in code_line.parts:
            key = token_ancestor(part.token, ancestor_list)
            colours = cls.palettes[palette][key]

            fg = cls.get_code(colored.fg, colours[0])
            attr = cls.get_code(colored.attr, colours[1])

            output.append(f'{fg}{attr}{bg}{part.text}{cls.reset}')

        return ''.join(output)

    @classmethod
    def line_number(cls, num):
        """Returns a colourized version of a line number"""
        fg = colored.fg('grey_39')
        return f'{fg}{num:3}{cls.reset} '
