"""
Virtual Screen (purdy.virtual.iscreen.py)
=========================================

This module mimics a code viewer, running through the requested actions and
making the final result available.
"""

from purdy.colour import RTFColourizer

# =============================================================================
# Screen
# =============================================================================

class CodeWidget:
    """Container for lines of code. This is a very simple implementation,
    wrapping a list of the lines.
    """
    def __init__(self):
        self.lines = []

    #--- RenderHook methods
    def line_inserted(self, listing, position, line):
        content = listing.render_line(line)
        index = position - 1
        self.lines.insert(index, content)

    def line_removed(self, listing, position):
        del self.lines[position - 1]

    def line_changed(self, listing, position, line):
        content = listing.render_line(line)
        index = position - 1
        self.lines[index] = content

    def clear(self):
        self.lines = []


class VirtualScreen:
    """Concrete, Urwid based implementation of a screen.

    :param parent_screen: :class:`purdy.ui.Screen` object that is creating
                          this concrete implementation

    """
    def __init__(self, parent_screen, **kwargs):
        self.parent_screen = parent_screen
        self.widgets = {}
        self.mode = 'plain'

        if kwargs.get('rtf', False):
            self.mode = 'rtf'

        self.background_colour = kwargs.get('background', None)


    def add_code_box(self, code_box):
        widget = CodeWidget()
        self.widgets[code_box] = widget
        code_box.listing.set_display(self.mode, widget)

    def add_twin_code_box(self, twin_code_box):
        widget = CodeWidget()
        self.widgets[twin_code_box.left.code_box] = widget
        twin_code_box.left.code_box.listing.set_display(self.mode, widget)

        widget = CodeWidget()
        self.widgets[twin_code_box.right.code_box] = widget
        twin_code_box.right.code_box.listing.set_display(self.mode, widget)

    def run(self):
        """Runs the actions on the code listings."""
        manager = self.parent_screen.animation_manager
        for cell in manager.cells:
            cell.render(manager, skip=True)

        if self.mode == 'rtf':
            if self.background_colour:
                RTFColourizer.set_background_colour(self.background_colour)

            print(RTFColourizer.rtf_header)

            for count, box in enumerate(self.parent_screen.code_boxes):
                widget = self.widgets[box]

                if count > 0:
                    print('\\\n')
                    print('\cf5 ' + 55*'=')
                    print('\\\n')
                    print('\\\n')

                for line in widget.lines:
                    print(line)
                    print('\\\n')

            print('}')
            return

        # else, plain mode
        for count, box in enumerate(self.parent_screen.code_boxes):
            widget = self.widgets[box]

            if count > 0:
                print(55*'=')

            for line in widget.lines:
                print(line)
