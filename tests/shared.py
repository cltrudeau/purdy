# tests/shared.py

from purdy.parser import CodeLine

# ===========================================================================

def code_liner(spec, newline, *args):
    line = CodeLine(spec, has_newline=newline)
    for arg in args:
        line.parts.append(arg)

    return line
