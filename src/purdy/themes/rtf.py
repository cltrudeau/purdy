from pygments.token import (Keyword, Name, Comment, String, Error,
    Number, Operator, Generic, Token, Whitespace, Punctuation, Literal)

from purdy.parser import LineNumber
from purdy.themes.utils import spawn_themes

# =============================================================================
# Theme colour maps for RTF based colourization
#
# Maps pygments Token to style attributes used in a span tag
#
# Maps a string to same for special use cases that aren't Tokens

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

    LineNumber:         '\\cf5 %s \n',
    'Background':       '\\cb1 ',
    'Highlight':        '\\cb13 ',
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


# =============================================================================

THEMES, ANCESTORS = spawn_themes(code=_code_palette, doc=_doc_palette,
    xml=_xml_palette)
