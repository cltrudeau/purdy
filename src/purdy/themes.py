# themes.py
from copy import copy

from pygments.token import (Keyword, Name, Comment, String, Error, Number,
    Operator, Generic, Token, Whitespace, Punctuation, Text, Literal)

from purdy.parser import HighlightOn, HighlightOff, Fold, LineNumber

# ===========================================================================
# Theme Class
# ===========================================================================

class Theme:
    def __init__(self, full_name, colour_map, inherit=None):
        self.full_name = full_name

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

no_colour = Theme("no_colour", {})

# ===========================================================================
# Default Themes
# ===========================================================================

default_code = Theme("default_code", {
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


default_doc = Theme("default_doc", {
    Name.Tag:           "cdcd00",
    Name.Attribute:     "cdcd00",
    Literal:            "88aaff",
    Generic.Heading:    "cdcd00",
    Generic.Subheading: "cdcd00",
    Generic.Emph:       "000087",
    Generic.Strong:     "005f00",
    String:             "8700af",
}, default_code)


default_xml = Theme("default_xml", {
    Name.Attribute: "cdcd00",
    Keyword:        "88aaff",
    Name.Tag:       "88aaff",
    Punctuation:    "88aaff",
}, default_code)

# ===========================================================================
# RTF Themes
# ===========================================================================

rtf_code = Theme("rtf_code", {
    Token:              "",
    Whitespace:         "",
    Comment:            ("8f5902", "", "italic"),
    Keyword:            ("2048a7", "", "bold"),
    Operator:           ("ce5c00", "", "bold"),
    Name:               "000000",
    Name.Builtin:       "3465a4",
    Name.Function:      "000000",
    Name.Class:         "000000",
    Name.Exception:     ("cc0000", "", "bold"),
    Name.Decorator:     ("5c35cc", "", "bold"),
    Name.Variable:      "",
    Name.Constant:      "",
    Name.Attribute:     "",
    Name.Tag:           "",
    Punctuation:        ("000000", "", "bold"),
    String:             "4e9a06",
    String.Doc:         ("8f5902", "", "italic"),
    Number:             ("0000cf", "", "bold"),
    Generic.Prompt:     "8f5902",
    Generic.Error:      "ef2929",
    Generic.Traceback:  ("a40000", "", "bold"),
    Error:              "ef2929",

    # Purdy tokens
    HighlightOn:         ("", "d5d5d5", ""),
    HighlightOff:        "",
    Fold:                "000000",
    LineNumber:          "000000",
})

rtf_xml = Theme("rtf_xml", {
    Name.Attribute: ("2048a7", "", "bold"),
    Name.Tag:       "3465a4",
    Keyword:        "3465a4",
    Punctuation:    "3465a4",
}, rtf_code)

rtf_doc = Theme("rtf_doc", {
    Generic.Emph:       "ef2929",
    Generic.Strong:     ("a40000", "", "bold"),
    Literal:            "",
    Generic.Heading:    "a40000",
    Generic.Subheading: "a40000",
}, rtf_code)

# ===========================================================================
# Python REPL Theme (as of 3.14)
# ===========================================================================

pyrepl_code = Theme("pyrepl_code", {
    Token:               "",
    Whitespace:          "",

    Comment:             "c91b00",
    Keyword:             ("6972ff", "", "bold"),
    Name.Builtin:        "00c5c8",
    Name.Builtin.Pseudo: "c7c7c7",
    Name.Class:          ("ffffff", "", "bold"),
    Name.Decorator:      "00c5c8",
    Name.Exception:      "00c5c8",
    Name.Function:       ("ffffff", "", "bold"),
    Number:              "c7c400",
    Punctuation.Marker:  ("ff6e67", "", "bold"),
    String:              "00c200",

    Operator:            "c7c7c7",
    Operator.Word:       ("6972ff", "", "bold"),
    Generic.Prompt:      ("ff77ff", "", "bold"),
    Generic.Error:       ("ff77ff", "", "bold"),
    Error:               ("cc0000", "", "bold"),
})

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
    "no_color": {
        "code": no_colour,
        "doc": no_colour,
        "xml": no_colour,
    },
    "rtf": {
        "code": rtf_code,
        "doc": rtf_doc,
        "xml": rtf_xml,
    },
    "pyrepl": {
        "code": pyrepl_code,
    },
}
