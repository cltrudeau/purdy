# purdy.tui.purdybox.py
from textual_transitions import Curtain

from purdy.content import Document
from purdy.renderers.textual import to_textual
from purdy.tui import animate
from purdy.tui.codebox import TextSection
from purdy.tui.widgets import PurdyContainer

# =============================================================================

class PurdyBox:
    """Groups the widgets used by the purdy app. In theory you could build
    your own Textual application with a purdy widget. In practice the library
    doesn't make that easy yet."""

    def __init__(self, row_specs, max_height=None):
        self.row_specs = row_specs
        self.rows = []

        self.container = PurdyContainer(self, row_specs, max_height)

    def transition(self, changes=None, speed=1):
        box_changes = {}
        if changes is None:
            changes = {}

        for codebox, content in changes.items():
            if content is None:
                codebox.doc = Document()
                box_changes[codebox] = ""
            else:
                if isinstance(content, str):
                    codebox.doc = Document(TextSection(content))
                else:
                    codebox.doc = Document(content)

                after = to_textual(codebox.doc)
                box_changes[codebox] = after

        tx = animate.ScreenTransitionCell(self, box_changes, Curtain,
            {"seconds":speed})
        animate.cell_list.append(tx)
        return self
