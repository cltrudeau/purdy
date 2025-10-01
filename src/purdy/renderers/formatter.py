# renderers/formatter.py
from purdy.content import Code, Document, RenderState
from purdy.parser import token_ancestor

# =============================================================================

def conversion_handler(formatter_cls, container, exceptions):
    """Helper function for the most common case of rendering a
    :class:`~purdy.content.Code` or :class:`~purdy.content.Document` object.

    :param formatter_cls: Reference to a class (not an object) to instantiate
        as the formatter for each section in the container
    :param container: :class:`~purdy.content.Code` or
        :class:`~purdy.content.Document` object to translate
    """
    if isinstance(container, Code):
        container = Document(container)

    render_state = RenderState(container)
    for section in container:
        formatter = formatter_cls(section, exceptions)
        render_state.formatter = formatter
        section.render(render_state)

    return render_state.content

# =============================================================================

class Formatter:
    """Base class for format tools."""
    def __init__(self, section, exceptions):
        self.tag_map = {}
        self.newline = "\n"
        self.escape = lambda x:x

        self.section = section
        self.exceptions = exceptions
        self._create_tag_map()
        self.ancestor_list = section.theme.colour_map.keys()

    def _create_tag_map(self):
        for token, fg, bg, attrs in self.section.theme.values():
            self._map_tag(token, fg, bg, attrs, self.exceptions)

    def _map_tag(self, token, fg, bg, attrs, exceptions):
        raise NotImplementedError()

    def render_code_line(self, render_state, line):
        """Abstract method that gets called for each code line to be rendered

        :param render_state: contains render info and results
        :param line: the line object being rendered
        """
        raise NotImplementedError()

# ---------------------------------------------------------------------------

class StrFormatter(Formatter):
    ### Uses str.format() to create stylized output from code; assumes the
    # ._map_tag() method populated using {text} for any token text to be
    # inserted
    def render_code_line(self, render_state, line):
        for part in line.parts:
            token = token_ancestor(part.token, self.ancestor_list)
            token_text = self.escape(part.text)

            try:
                marker = self.tag_map[token]
                render_state.content += marker.format(text=token_text)
            except KeyError:
                render_state.content += token_text

        if line.has_newline:
            render_state.content += self.newline
