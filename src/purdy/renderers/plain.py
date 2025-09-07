# renderers/plain.py
from purdy.content import Code, MultiCode
from purdy.renderers.formatter import Formatter

class PlainFormatter(Formatter):
    def format_line(self, line, ancestor_list):
        result = ""
        for part in line.parts:
            result += part.text

        if line.has_newline:
            result += "\n"

        return result

def to_plain(container):
    """Transforms tokenized content in a :class:`Code` object into a plain
    text string.

    :param container: `Code` or :class:`MultiCode` object to render
    """
    result = ""
    formatter = PlainFormatter()

    if isinstance(container, Code):
        container = MultiCode(container)

    for code_index in range(0, len(container)):
        result += formatter.format_doc(container, code_index)

    return result
