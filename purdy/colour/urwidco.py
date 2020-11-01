from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace, Punctuation

from .base import BaseColourizer
from purdy.parser import FoldedCodeLine, token_ancestor

# =============================================================================
# Urwid Colourizer

class UrwidColourizer(BaseColourizer):
    palettes = {
        'code': {
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
        },
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
            ('folded', 'white', '', '', 'white', ''),
            ('line_number', 'dark gray', '', '', 'dark gray', ''),
            ('empty', '', '', '', '', ''),
            ('empty_highlight', '', 'light gray', '', '', 'g23'),
        ])
        
        return urwid_palette

    def colourize_part(self, code_part, highlight):
        ancestor_list = self.palettes[self.palette].keys()
        ancestor = token_ancestor(code_part.token, ancestor_list)
        key = f'{self.palette}_{ancestor}' 
        if highlight:
            key += '_highlight'

        markup = (key, code_part.text)
        return markup

    def colourize(self, code_line):
        """Returns a list containing markup tuples as used by urwid.Text
        widgets.

        :param code_line: a :class:`CodeLine`   object to colourize
        """
        if isinstance(code_line, FoldedCodeLine):
            return ('folded', '     ⋮')

        ancestor_list = self.palettes[self.palette].keys()

        output = []
        if code_line.line_number >= 0:
            output.append( self.line_number(code_line.line_number) )

        for part in code_line.parts:
            ancestor = token_ancestor(part.token, ancestor_list)
            key = f'{self.palette}_{ancestor}' 

            if code_line.highlight:
                key += '_highlight'

            # Urwid uses a palette which has been built as a hash using the
            # names of the ancestor tokens as keys and the fg/bg colour
            # choices as values, each piece of marked up text is a tuple of
            # the palette key and the text to display
            markup = (key, part.text)
            output.append(markup)

        return output

    def line_number(self, num):
        """Returns a colourized version of a line number"""
        return ('line_number', f'{num:3} ')
