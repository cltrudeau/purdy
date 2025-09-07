# tests/shared.py
from pathlib import Path

from purdy.content import Code, MultiCode
from purdy.parser import CodeLine
from purdy.renderers.rich import to_rich
from purdy.renderers.html import to_html
from purdy.renderers.rtf import to_rtf
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

def _multicode_factory(theme=None):
    path = (Path(__file__).parent / Path("data/code.py")).resolve()
    code = Code(str(path))
    if theme is not None:
        code.theme = theme

    mc = MultiCode(code)
    mc.wrap = 80
    mc.line_numbers_enabled = True
    mc.starting_line_number = 5
    code.highlight(2, "17:8,5")   # 3:pass, 18:while
    code.fold(6, 4)               # 7-11: __init__ method
    return mc


def generate_rich():
    mc = _multicode_factory()
    text = to_rich(mc)
    return text


def generate_html():
    mc = _multicode_factory()
    text = to_html(mc, snippet=False)
    return text


def generate_rtf():
    theme = THEME_MAP["rtf"]["code"]
    mc = _multicode_factory(theme)
    text = to_rtf(mc)
    return text
