# renderers/plain.py
from purdy.content import Code, Document, RenderState

class PlainFormatter:
    def render_code_line(self, render_state, line):
        result = ""
        for part in line.parts:
            result += part.text

        if line.has_newline:
            result += "\n"

        render_state.content += result


def to_plain(container):
    """Renders content without any formatting.

    :param container: :class:`Document` or :class:`Code` content to be
        rendered

    :returns: rendered string
    """
    if isinstance(container, Code):
        container = Document(container)

    render_state = RenderState(container)
    render_state.formatter = PlainFormatter()
    for section in container:
        section.render(render_state)

    return render_state.content
