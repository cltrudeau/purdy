# tests/shared.py
from pathlib import Path

from purdy.content import Code
from purdy.parser import CodeLine
from purdy.renderers.rich import to_rich
from purdy.renderers.html import to_html
from purdy.renderers.rtf import to_rtf
from purdy.motif import Motif
from purdy.themes import THEME_MAP

# ===========================================================================

RENDER_TESTS = ["rich", "html", "rtf"]

# ===========================================================================

def code_liner(spec, newline, *args):
    line = CodeLine(spec, has_newline=newline)
    for arg in args:
        line.parts.append(arg)

    return line

# ===========================================================================
# Renderer Testing
# ===========================================================================

def _motif_factory(theme=None):
    path = (Path(__file__).parent / Path("data/code.py")).resolve()
    motif = Motif(Code(str(path)), theme)
    motif.wrap = 80
    motif.line_numbers_enabled = True
    motif.starting_line_number = 5
    motif.highlight(2, "17:8,5")   # 3:pass, 18:while
    motif.fold(6, 4)               # 7-11: __init__ method
    return motif


def generate_rich():
    motif = _motif_factory()
    text = to_rich(motif)
    return text


def generate_html():
    motif = _motif_factory()
    text = to_html(motif, snippet=False)
    return text


def generate_rtf():
    theme = THEME_MAP["rtf"]["code"]
    motif = _motif_factory(theme)
    text = to_rtf(motif)
    return text
