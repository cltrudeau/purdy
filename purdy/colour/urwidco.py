from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace, Punctuation, Text, Literal

from purdy.parser import FoldedCodeLine, token_ancestor

# =============================================================================
# Urwid Colourizer

_code_palette = {
    # urwid colour spec supports both 16 and 256 colour terminals
    #                    fg16            bg16    fg256   bg256
    Token:              ('',             '', '', '',             ''),
    Whitespace:         ('',             '', '', '',             ''),
    Comment:            ('dark cyan',    '', '', '#6dd',         ''),
    Keyword:            ('brown',        '', '', '#d8d',         ''),
    Operator:           ('brown',        '', '', '#aaa',         ''),
    Punctuation:        ('dark cyan',    '', '', '#8df',         ''),
    Text:               ('dark cyan',    '', '', '#ddd',         ''),
    Name:               ('light gray',   '', '', '#ddd',         ''), 
    Name.Builtin:       ('dark cyan',    '', '', '#8af',    ''), 
    Name.Builtin.Pseudo:('dark cyan',    '', '', '#a66,bold',    ''), 
    Name.Function:      ('dark cyan',    '', '', '#adf',   ''),
    Name.Class:         ('dark cyan',    '', '', '#adf',   ''),
    Name.Exception:     ('dark green',   '', '', '#fd6,bold',   ''),
    Name.Decorator:     ('dark cyan',    '', '', '#fd6,bold',    ''),
    String:             ('dark magenta', '', '', '#ddd', ''),
    Number:             ('dark magenta', '', '', '#f86', ''),
    Generic.Prompt:     ('dark blue',    '', '', '#fff,bold',    ''),
    Generic.Error:      ('dark green',   '', '', '#fd6,bold',   ''),
    Generic.Traceback:  ('',             '', '', '#ddd',    ''),
    Error:              ('dark green',   '', '', '#fd6,bold',         ''),
}

_xml_palette = dict(_code_palette)
_xml_palette.update({
    Name.Attribute: ('brown',        '', '', 'brown',        ''),
    Keyword:        ('dark cyan',    '', '', '#8af',         ''),
    Name.Tag:       ('dark cyan',    '', '', '#8af',         ''),
    Punctuation:    ('dark cyan',    '', '', '#8af',         ''),
})

_doc_palette = dict(_code_palette)
_doc_palette.update({
    Name.Tag:       ('brown',        '', '', 'brown',        ''),
    Name.Attribute: ('brown',        '', '', 'brown',        ''),
    Literal:        ('dark cyan',    '', '', '#8af',         ''),
    Generic.Heading:('brown',        '', '', 'brown',        ''),
    Generic.Subheading:('brown',        '', '', 'brown',        ''),
    Generic.Emph:   ('dark blue',    '', '', 'dark blue',        ''),
    Generic.Strong: ('dark green',   '', '', 'dark green',        ''),
    String:         ('dark magenta', '', '', 'dark magenta',        ''),
})

class UrwidColourizer:
    palettes = {
        'code':_code_palette,
        'xml':_xml_palette,
        'doc':_doc_palette,
    }

    @classmethod
    def create_urwid_palette(cls):
        """Returns a list of colour tuples that Urwid uses as its palette. The
        list is based on the UrwidColourizer.colours with a couple extra items
        """
        urwid_palette = []
        for name, palette in cls.palettes.items():

            for key, value in palette.items():
                # for each item in our colours hash create a tuple consisting of
                # the token name and its values
                item = (f'{name}_{key}', ) + value
                urwid_palette.append( item )

                # do it again for highlighted tokens, for 16 colour mode change
                # both the fg and bg colour, for 256 colour mode just change the
                # background
                item = (f'{name}_{key}_highlight', 'black', 'light gray', '', 
                    value[3], 'g23')
                urwid_palette.append( item )

        # add miscellaneous other palette items
        urwid_palette.extend([
            ('reverse', 'black', 'white', '', 'black', 'white'),
            ('bold', 'white,bold', '', '', 'white,bold', ''),
            ('title', 'white,underline', '', '', 'white,underline', ''),
            ('folded', 'white', '', '', 'white', ''),
            ('line_number', 'dark gray', '', '', 'dark gray', ''),
            ('empty', '', '', '', '', ''),
            ('empty_highlight', '', 'light gray', '', '', 'g23'),
        ])
        
        return urwid_palette

    @classmethod
    def colourize(cls, code_line):
        """Returns a list containing markup tuples as used by urwid.Text
        widgets.

        :param code_line: a :class:`CodeLine`   object to colourize
        """
        if isinstance(code_line, FoldedCodeLine):
            return ('folded', '     ⋮')

        palette = code_line.lexer.palette
        ancestor_list = cls.palettes[palette].keys()

        output = []
        if code_line.line_number >= 0:
            output.append( cls.line_number(code_line.line_number) )

        for part in code_line.parts:
            ancestor = token_ancestor(part.token, ancestor_list)
            key = f'{palette}_{ancestor}' 

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
