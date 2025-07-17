# renderers/rich_co.py
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace, Punctuation, Text, Literal

from purdy.parser import (HighlightOn, HighlightOff, Fold, LineNumber,
    token_ancestor)
from purdy.renderers.utils import percent_s_formatter, format_setup

# ===========================================================================

_code_theme = {
    Token:              "",
    Whitespace:         "",
    Comment:            "[#66dddd]%s[/]",
    Keyword:            "[#dd88dd]%s[/]",
    Keyword.Constant:   "[green]%s[/]",
    Operator:           "[#aaaaaa]%s[/]",
    Punctuation:        "[#88ddff]%s[/]",
    Text:               "[#dddddd]%s[/]",
    Name:               "[#dddddd]%s[/]",
    Name.Builtin:       "[#88aaff]%s[/]",
    Name.Builtin.Pseudo:"[#aa6666 bold]%s[/]",
    Name.Function:      "[#aaddff]%s[/]",
    Name.Class:         "[#aaddff]%s[/]",
    Name.Exception:     "[#ffdd66 bold]%s[/]",
    Name.Decorator:     "[#ffdd66 bold]%s[/]",
    String:             "[#dddddd]%s[/]",
    Number:             "[#ff8866]%s[/]",
    Generic.Prompt:     "[#ffffff bold]%s[/]",
    Generic.Error:      "[#ffdd66 bold]%s[/]",
    Generic.Traceback:  "[#dddddd]%s[/]",
    Error:              "[#ffdd66 bold]%s[/]",

    # Purdy tokens
    HighlightOn:        "[reverse]%s",
    HighlightOff:       "[/reverse]",
    Fold:               "[white]%s[/]",
    LineNumber:         "[#7f7f7f]%s[/]",
}


_xml_theme = dict(_code_theme)
_xml_theme.update({
    Name.Attribute: "[#cdcd00]%s[/]",
    Keyword:        "[#88aaff]%s[/]",
    Name.Tag:       "[#88aaff]%s[/]",
    Punctuation:    "[#88aaff]%s[/]",
})


_doc_theme = dict(_code_theme)
_doc_theme.update({
    Name.Tag:           "[#cdcd00]%s[/]",
    Name.Attribute:     "[#cdcd00]%s[/]",
    Literal:            "[#88aaff]%s[/]",
    Generic.Heading:    "[#cdcd00]%s[/]",
    Generic.Subheading: "[#cdcd00]%s[/]",
    Generic.Emph:       "[dark_blue]%s[/]",
    Generic.Strong:     "[dark_green]%s[/]",
    String:             "[dark_magenta]%s[/]",
})


themes = {
    "code": _code_theme,
    "xml": _xml_theme,
    "doc": _doc_theme,
}

# ===========================================================================

def rich_xfrm(code, theme="code", no_colour=False):
    """Transforms tokenized content in a :class:`Code` object into a string
    with Rich library formatting.

    :param code: `Code` object to translate
    :param theme: String for built-in theme name, or dictionary with Rich
        Token:colour attributes pairs
    """
    theme, ancestor_list = format_setup(no_colour, theme, themes)
    result = percent_s_formatter(code, theme, ancestor_list)
    return result
