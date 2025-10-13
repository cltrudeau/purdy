# purdy.tui.tuicontent.py
from textual.content import Content as TContent

from purdy.content import Section
from purdy.parser import LineNumber
from purdy.themes import THEME_MAP

# =============================================================================
# Content Abstractions
# =============================================================================

class EscapeText(str):
    """Class to distinguish plain text from Textual markup to present escaped
    text."""
    pass


class TextSection(Section):
    """Abstracts one or more lines of Textual markup strings"""
    default_theme_name = "default"
    default_theme_category = "code"

    def __init__(self, content=None, theme=None):
        super().__init__()

        # Set the content
        if content is None:
            self.lines = []
        elif isinstance(content, (str, EscapeText)):
            self.lines = [content, ]
        elif isinstance(content, list):
            self.lines = content
        else:
            raise ValueError("TextSection requires string or list of strings")

        # Configure Theme
        if theme is None:
            theme = self.default_theme_name

        if isinstance(theme, str):
            self.theme = THEME_MAP[theme][self.default_theme_category]
        else:
            self.theme = theme

    def render_line(self, render_state, line, line_index):
        if render_state.doc.line_numbers_enabled:
            num = render_state.next_line_number()
            render_state.content += render_state.formatter.part_to_content(
                LineNumber, num)

        if isinstance(line, EscapeText):
            render_state.content += TContent.from_markup("$text", text=line)
        else:
            render_state.content += TContent.from_markup(line)

        render_state.content += "\n"
