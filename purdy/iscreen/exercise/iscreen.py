"""
Exercise Screen (purdy.Exercise.iscreen.py)
===========================================

This module mimics a code viewer, capturing the picture of every code box in
the screen at every step. Used for testing actions and steps.
"""

# =============================================================================
# Screen
# =============================================================================

class FlipBook:
    def __init__(self):
        self.pages = []

    def add_page(self, code_box, change_type, content):
        data = {
            'code_box':f'CodeBox(id={code_box.id})',
            'change_type':change_type,
            'content':content,
        }
        self.pages.append(data)


class ExerciseCodeWidget:
    """Render hook implementation that stores actions as flip books.
    """
    def __init__(self, flipbook, code_book_count):
        self.lines = []
        self.flipbook = flipbook

        self.id = code_book_count

    #--- RenderHook methods
    def line_inserted(self, listing, position, line):
        content = listing.render_line(line)
        index = position - 1
        self.lines.insert(index, content)
        
        self.flipbook.add_page(self, f'insert:{position}', content)

    def line_removed(self, listing, position):
        del self.lines[position - 1]

        self.flipbook.add_page(self, f'remove:{position}', '')

    def line_changed(self, listing, position, line):
        content = listing.render_line(line)
        index = position - 1
        self.lines[index] = content

        self.flipbook.add_page(self, f'change:{position}', content)

    def clear(self):
        self.lines = []

        self.flipbook.add_page(self, 'clear', '')


class ExerciseScreen:
    """Concrete implementation of a screen that captures each change to its
    codeboxes in "flip book pages". Each page can be thought of a step in the
    animations used to create the pages. Nothing is displayed, this is used
    for testing.

    :param parent_screen: :class:`purdy.ui.Screen` object that is creating
                          this concrete implementation
    """
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        self.widgets = {}
        self.flipbook = FlipBook()
        self.mode = 'plain'
        self.code_book_count = 0

    def add_code_box(self, code_box):
        self.code_book_count += 1
        widget = ExerciseCodeWidget(self.flipbook, self.code_book_count)
        self.widgets[code_box] = widget
        code_box.listing.set_display(self.mode, widget)

    def add_twin_code_box(self, twin_code_box):
        self.code_book_count += 1
        widget = ExerciseCodeWidget(self.flipbook, self.code_book_count)
        self.widgets[twin_code_box.left.code_box] = widget
        twin_code_box.left.code_box.listing.set_display(self.mode, widget)

        self.code_book_count += 1
        widget = ExerciseCodeWidget(self.flipbook, self.code_book_count)
        self.widgets[twin_code_box.right.code_box] = widget
        twin_code_box.right.code_box.listing.set_display(self.mode, widget)

    def set_alarm(self, handler, when):
        pass

    def remove_alarm(self, alarm_handle):
        pass

    def run(self):
        """Runs the actions on the code listings."""
        manager = self.parent_screen.animation_manager
        # Run through the steps forward, then backwards then forward again
        self.flipbook.pages.append('=== Actions ===')
        for action in self.parent_screen.actions:
            self.flipbook.pages.append(str(action))

        self.flipbook.pages.append('=== Steps ===')
        for cell in manager.cells:
            for step in cell.steps:
                self.flipbook.pages.append(str(step))

        self.flipbook.pages.append('=== Forward ===')
        for cell in manager.cells:
            cell.render(manager, skip=True)

        self.flipbook.pages.append('=== Backward ===')
        for cell in reversed(manager.cells):
            cell.undo(manager)

        self.flipbook.pages.append('=== Forward ===')
        for cell in manager.cells:
            cell.render(manager, skip=True)
