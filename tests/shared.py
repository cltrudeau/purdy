# tests/shared.py
from pathlib import Path

from purdy.content import Code
from purdy.parser import CodeLine
from purdy.renderers.rich import to_rich
from purdy.renderers.html import to_html
from purdy.style import Style

# ===========================================================================

RENDER_TESTS = ["rich", "html"]

# ===========================================================================

def code_liner(spec, newline, *args):
    line = CodeLine(spec, has_newline=newline)
    for arg in args:
        line.parts.append(arg)

    return line

# ===========================================================================
# Renderer Testing
# ===========================================================================

def _style_factory():
    path = (Path(__file__).parent / Path("data/code.py")).resolve()
    style = Style(Code(str(path)))
    style.wrap = 80
    style.line_numbers_enabled = True
    style.starting_line_number = 5
    style.highlight(2, "17:8,5")   # 3:pass, 18:while
    style.fold(6, 4)               # 7-11: __init__ method
    return style


def generate_rich():
    style = _style_factory()
    text = to_rich(style)
    return text


def generate_html():
    style = _style_factory()
    text = to_html(style, snippet=False)
    return text
