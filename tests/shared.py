# tests/shared.py
from pathlib import Path

from purdy.content import Code, Document
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

def _doc_factory(theme=None):
    path = (Path(__file__).parent / Path("data/code.py")).resolve()
    code = Code(str(path))
    if theme is not None:
        code.theme = theme

    code.highlight(2, "17:8,5")   # 3:pass, 18:while
    code.fold(6, 4)               # 7-11: __init__ method
    doc = Document(code)
    doc.wrap = 80
    doc.line_numbers_enabled = True
    doc.starting_line_number = 5
    return doc


def generate_rich():
    doc = _doc_factory()
    text = to_rich(doc)
    return text


def generate_html():
    doc = _doc_factory()
    text = to_html(doc, snippet=False)
    return text


def generate_rtf():
    theme = THEME_MAP["rtf"]["code"]
    doc = _doc_factory(theme)
    text = to_rtf(doc)
    return text
