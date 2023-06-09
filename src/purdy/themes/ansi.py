from pygments.token import (Keyword, Name, Comment, String, Error,
    Number, Operator, Generic, Token, Whitespace, Punctuation, Text, Literal)

from purdy.parser import LineNumber
from purdy.themes.utils import spawn_themes

# =============================================================================
# Theme colour maps for ANSI based colourization
#
# Maps pygments Token to a 256-colour foreground, or a tuple indicating
# foreground and attribute.
#
# Maps a string to same for special use cases that aren't Tokens

_code_palette = {
    #                    fg256         attr
    Token:              '',
    Whitespace:         '',
    Comment:            'cyan',
    Keyword:            'yellow',
    Operator:           'yellow',
    Name:               'light_gray',
    Name.Builtin:       '#006688',
    Name.Function:      'light_gray',
    Name.Namespace:     'light_gray',
    Name.Class:         'light_gray',
    Name.Exception:     'dark_green',
    Name.Decorator:     ('#6666dd', 'bold',),
    Name.Variable:      '',
    Name.Constant:      '',
    Name.Attribute:     '',
    Name.Tag:           '',
    String:             'magenta',
    Number:             'magenta',
    Generic.Prompt:     'dark_blue',
    Generic.Error:      'dark_green',
    Generic.Traceback:  ('#aa0000', 'bold',),
    Error:              '#ff0000',

    LineNumber:         'grey_39',
    'Background':       '',
    'Highlight':        'grey_23',
}

_doc_palette = dict(_code_palette)
_doc_palette.update({
    Text:               'light_gray',
    Name.Tag:           '#006688',
    Name.Attribute:     '#006688',
    Punctuation:        '#006688',
    Generic.Heading:    'yellow',
    Generic.Subheading: 'yellow',
    Literal:            'magenta',
    Generic.Emph:       'dark_blue',
    Generic.Strong:     ('dark_green', 'bold',),
})

_xml_palette = dict(_code_palette)
_xml_palette.update({
    Name.Attribute: 'yellow',
    Keyword:        'light_slate_blue',
    Name.Tag:       'light_slate_blue',
    Punctuation:    'light_slate_blue',
})

# =============================================================================

THEMES, ANCESTORS = spawn_themes(code=_code_palette, doc=_doc_palette,
    xml=_xml_palette)
