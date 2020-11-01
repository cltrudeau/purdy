"""
Colour Module (purdy.colour)
===============================

Contains classes to convert tokens to colour according to the various
supported renderers and palettes.
"""

from . import plainco, ansico, htmlco, rtfco, urwidco

COLOURIZERS = {
    'plain':plainco.PlainColourizer,
    'ansi':ansico.ANSIColourizer,
    'html':htmlco.HTMLColourizer,
    'rtf':rtfco.RTFColourizer,
    'urwid':urwidco.UrwidColourizer,
}
