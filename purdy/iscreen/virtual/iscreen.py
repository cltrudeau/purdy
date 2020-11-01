"""
Virtual Screen (purdy.virtual.iscreen.py)
=========================================

This module mimics a code viewer, running through the requested actions and
making the final result available.
"""

from purdy.colour import COLOURIZERS
from purdy.ui import VirtualCodeWidget

RTFColourizer = COLOURIZERS['rtf']

# =============================================================================
# Screen
# =============================================================================

class VirtualScreen:
    """Concrete, Urwid based implementation of a screen.

    :param parent_screen: :class:`purdy.ui.Screen` object that is creating
                          this concrete implementation

    """
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        self.widgets = {}
        self.mode = 'plain'
        if parent_screen.args.exportrtf:
            self.mode = 'rtf'

        self.background_colour = parent_screen.args.background

    def add_code_box(self, code_box):
        widget = VirtualCodeWidget()
        self.widgets[code_box] = widget
        code_box.listing.set_display(self.mode, widget)

    def add_twin_code_box(self, twin_code_box):
        widget = VirtualCodeWidget()
        self.widgets[twin_code_box.left.code_box] = widget
        twin_code_box.left.code_box.listing.set_display(self.mode, widget)

        widget = VirtualCodeWidget()
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
