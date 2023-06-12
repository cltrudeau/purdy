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
    Comment:            '6',                 # cyan
    Keyword:            '3',                 # yellow
    Operator:           '3',                 # yellow
    Name:               '7',                 # light gray
    Name.Builtin:       '24',                # deep sky blue 4b
    Name.Function:      '7',                 # light gray
    Name.Namespace:     '7',
    Name.Class:         '7',
    Name.Exception:     '22',                # dark green
    Name.Decorator:     ('62', 'bold',),     # slate_blue 3b
    Name.Variable:      '',
    Name.Constant:      '',
    Name.Attribute:     '',
    Name.Tag:           '',
    String:             '5',                 # magenta
    Number:             '5',
    Generic.Prompt:     '18',                # dark_blue
    Generic.Error:      '22',                # dark green
    Generic.Traceback:  ('124', 'bold',),    # red 3a
    Error:              '9',                 # light red

    LineNumber:         '241',               # grey 39
    'Background':       '',
    'Highlight':        '237',               # grey 23
}

_doc_palette = dict(_code_palette)
_doc_palette.update({
    Text:               '7',                # light grey
    Name.Tag:           '24',               # deep sky blue 4b
    Name.Attribute:     '24',
    Punctuation:        '24',
    Generic.Heading:    '3',                # yellow
    Generic.Subheading: '3',
    Literal:            '5',                # magenta
    Generic.Emph:       '18',               # dark blue
    Generic.Strong:     ('22', 'bold',),    # dark green
})

_xml_palette = dict(_code_palette)
_xml_palette.update({
    Name.Attribute: '3',              # yellow
    Keyword:        '105',            # light_slate_blue
    Name.Tag:       '105',
    Punctuation:    '105',
})

# =============================================================================

THEMES, ANCESTORS = spawn_themes(code=_code_palette, doc=_doc_palette,
    xml=_xml_palette)
