# renderers/rich_co.py
from pygments.token import Keyword, Name, Comment, String, Error, \
    Number, Operator, Generic, Token, Whitespace, Punctuation, Text, Literal

from purdy.parser import (HighlightOn, HighlightOff, Fold, LineNumber,
    token_ancestor)

# ===========================================================================

_code_theme = {
    Token:              "",
    Whitespace:         "",
    Comment:            "[#66dddd]",
    Keyword:            "[#dd88dd]",
    Keyword.Constant:   "[green]",
    Operator:           "[#aaaaaa]",
    Punctuation:        "[#88ddff]",
    Text:               "[#dddddd]",
    Name:               "[#dddddd]",
    Name.Builtin:       "[#88aaff]",
    Name.Builtin.Pseudo:"[#aa6666 bold]",
    Name.Function:      "[#aaddff]",
    Name.Class:         "[#aaddff]",
    Name.Exception:     "[#ffdd66 bold]",
    Name.Decorator:     "[#ffdd66 bold]",
    String:             "[#dddddd]",
    Number:             "[#ff8866]",
    Generic.Prompt:     "[#ffffff bold]",
    Generic.Error:      "[#ffdd66 bold]",
    Generic.Traceback:  "[#dddddd]",
    Error:              "[#ffdd66 bold]",

    # Purdy tokens
    HighlightOn:        "[reverse]",
    HighlightOff:       "[/reverse]",
    Fold:               "[white]",
    LineNumber:         "[#7f7f7f]",
}


_xml_theme = dict(_code_theme)
_xml_theme.update({
    Name.Attribute: "[#cdcd00]",
    Keyword:        "[#88aaff]",
    Name.Tag:       "[#88aaff]",
    Punctuation:    "[#88aaff]",
})


_doc_theme = dict(_code_theme)
_doc_theme.update({
    Name.Tag:           "[#cdcd00]",
    Name.Attribute:     "[#cdcd00]",
    Literal:            "[#88aaf]f",
    Generic.Heading:    "[#cdcd00]",
    Generic.Subheading: "[#cdcd00]",
    Generic.Emph:       "[dark_blue]",
    Generic.Strong:     "[dark_green]",
    String:             "[dark_magenta]",
})


themes = {
    "code": _code_theme,
    "xml": _xml_theme,
    "doc": _doc_theme,
}

# ===========================================================================

def rich_xfrm(code, theme="code"):
    """Transforms tokenized content in a :class:`Code` object into a string
    with Rich library formatting.

    :param code: `Code` object to translate
    :param theme: String for built-in theme name, or dictionary with Rich
        Token:colour attributes pairs
    """
    if isinstance(theme, str):
        theme = themes[theme]

    ancestor_list = theme.keys()

    result = ""
    for line in code:
        for part in line.parts:
            token = token_ancestor(part.token, ancestor_list)
            marker = theme[token]
            result += marker + part.text
            if marker:
                result += "[/]"

        if line.has_newline:
            result += "\n"

    return result
