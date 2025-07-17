# renderers/html_xfrm.py
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace, Punctuation, Text, Literal

from purdy.parser import (HighlightOn, HighlightOff, Fold, LineNumber,
    token_ancestor)
from purdy.renderers.utils import percent_s_formatter, format_setup

# ===========================================================================

_code_theme = {
    Token:              '',
    Whitespace:         '',
    Comment:            '<span style="color: #66dddd;>"%s</span>',
    Keyword:            '<span style="color: #dd88dd">%s</span>',
    Keyword.Constant:   '<span style="color: green">%s</span>',
    Operator:           '<span style="color: #aaaaaa">%s</span>',
    Punctuation:        '<span style="color: #88ddff">%s</span>',
    Text:               '<span style="color: #dddddd">%s</span>',
    Name:               '<span style="color: #dddddd">%s</span>',
    Name.Builtin:       '<span style="color: #88aaff">%s</span>',
    Name.Builtin.Pseudo:'<span style="color: #aa6666"><b>%s</b></span>',
    Name.Function:      '<span style="color: #aaddff">%s</span>',
    Name.Class:         '<span style="color: #aaddff">%s</span>',
    Name.Exception:     '<span style="color: #ffdd66"><b>%s</b></span>',
    Name.Decorator:     '<span style="color: #ffdd66"><b>%s</b></span>',
    String:             '<span style="color: #dddddd">%s</span>',
    Number:             '<span style="color: #ff8866">%s</span>',
    Generic.Prompt:     '<span style="color: #ffffff"><b>%s</b></span>',
    Generic.Error:      '<span style="color: #ffdd66"><b>%s</b></span>',
    Generic.Traceback:  '<span style="color: #dddddd">%s</span>',
    Error:              '<span style="color: #ffdd66"><b>%s</b></span>',

    # Purdy tokens
    HighlightOn:        '<span style="background: white;">%s</span>',
    HighlightOff:       '</span>',
    Fold:               '<span style="color: white">%s</span>',
    LineNumber:         '<span style="color: #7f7f7f">%s</span>',
}


_xml_theme = dict(_code_theme)
_xml_theme.update({
    Name.Attribute: '<span style="color: #cdcd00">%s</span>',
    Keyword:        '<span style="color: #88aaff">%s</span>',
    Name.Tag:       '<span style="color: #88aaff">%s</span>',
    Punctuation:    '<span style="color: #88aaff">%s</span>',
})


_doc_theme = dict(_code_theme)
_doc_theme.update({
    Name.Tag:           '<span style="color: #cdcd00">%s</span>',
    Name.Attribute:     '<span style="color: #cdcd00">%s</span>',
    Literal:            '<span style="color: #88aaff">%s</span>',
    Generic.Heading:    '<span style="color: #cdcd00">%s</span>',
    Generic.Subheading: '<span style="color: #cdcd00">%s</span>',
    Generic.Emph:       '<span style="color: dark_blue">%s</span>',
    Generic.Strong:     '<span style="color: dark_green">%s</span>',
    String:             '<span style="color: dark_magenta">%s</span>',
})


themes = {
    "code": _code_theme,
    "xml": _xml_theme,
    "doc": _doc_theme,
}

# ===========================================================================

HTML_HEADER = """\
<!doctype html>
<html lang="en">
<body>
"""

HTML_FOOTER = """\
</body>
</html>
"""

def html_xfrm(code, theme="code", no_colour=False, snippet=True):
    """Transforms tokenized content in a :class:`Code` object into a string
    representation of HTML.

    :param code: `Code` object to translate
    :param theme: String for built-in theme name, or dictionary with Rich
        Token:colour attributes pairs
    :param snippet: When True [default] only show the code in a <div>,
        otherwise wrap it in full HTML document tags.
    """
    theme, ancestor_list = format_setup(no_colour, theme, themes)

    result = ""

    # Header
    if not snippet:
        result += HTML_HEADER

    result += (
        '<div style="background :#222222; overflow:auto; width:auto; '
        'border:solid gray; border-width:.1em .1em .1em .8em; '
        'padding:.2em .6em;"><pre style="margin: 0; line-height:125%">'
    )

    result += percent_s_formatter(code, theme, ancestor_list)

    if not snippet:
        result += HTML_FOOTER

    return result
