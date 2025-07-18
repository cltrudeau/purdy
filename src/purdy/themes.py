# themes.py
from copy import copy

from pygments.token import (Keyword, Name, Comment, String, Error, Number,
    Operator, Generic, Token, Whitespace, Punctuation, Text, Literal)

from purdy.parser import HighlightOn, HighlightOff, Fold, LineNumber

# ===========================================================================
# Theme Class
# ===========================================================================

class Theme:
    def __init__(self, colour_map, inherit=None):
        if inherit is not None:
            # Inherit from another theme
            self.colour_map = copy(inherit.colour_map)
        else:
            self.colour_map = {}

        self.colour_map.update(colour_map)

    def values(self):
        for key, value in self.colour_map.items():
            if isinstance(value, tuple):
                fg, bg, attrs = value
            else:
                fg = value
                bg = ""
                attrs = ""

            yield key, fg, bg, attrs

# ===========================================================================
# Empty Theme
# ===========================================================================

no_colour = Theme({})

# ===========================================================================
# Default Themes
# ===========================================================================

default_code = Theme({
    Token:               "",
    Whitespace:          "",
    Comment:             "66dddd",
    Keyword:             "dd88dd",
    Keyword.Constant:    "008000",
    Operator:            "aaaaaa",
    Punctuation:         "88ddff",
    Text:                "dddddd",
    Name:                "dddddd",
    Name.Builtin:        "88aaff",
    Name.Builtin.Pseudo: ("aa6666", "", "bold"),
    Name.Function:       "aaddff",
    Name.Class:          "aaddff",
    Name.Exception:      ("ffdd66", "", "bold"),
    Name.Decorator:      ("ffdd66", "", "bold"),
    String:              "dddddd",
    Number:              "ff8866",
    Generic.Prompt:      ("ffffff", "", "bold"),
    Generic.Error:       ("ffdd66", "", "bold"),
    Generic.Traceback:   "dddddd",
    Error:               ("ffdd66", "", "bold"),

    # Purdy tokens
    HighlightOn:         ("", "ffffff", ""),
    HighlightOff:        "",
    Fold:                "ffffff",
    LineNumber:          "7f7f7f",
})


default_doc = Theme({
    Name.Tag:           "cdcd00",
    Name.Attribute:     "cdcd00",
    Literal:            "88aaff",
    Generic.Heading:    "cdcd00",
    Generic.Subheading: "cdcd00",
    Generic.Emph:       "000087",
    Generic.Strong:     "005f00",
    String:             "8700af",
}, default_code)


default_xml = Theme({
    Name.Attribute: "cdcd00",
    Keyword:        "88aaff",
    Name.Tag:       "88aaff",
    Punctuation:    "88aaff",
}, default_code)

# ===========================================================================
# Theme Map
# ===========================================================================

THEME_MAP = {
    "default": {
        "code": default_code,
        "doc": default_doc,
        "xml": default_xml,
    },
    "no_colour": {
        "code": no_colour,
        "doc": no_colour,
        "xml": no_colour,
    },
}
