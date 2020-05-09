"""
Content
-------

Reperesntations of source code are found in this module.
"""
import os
from copy import copy

from purdy.colour import COLOURIZERS
from purdy.parser import parse_source

# =============================================================================

class Code:
    """Represents source code from the user."""

    def __init__(self, filename='', text='', lexer_name='detect'):
        """Constructor

        :param filename: name of a file to read for content. If both this and 
                         `text` is given, `filename` is used first
        :param text: a string containing code
        :param lexer_name: name of lexer to use to tokenize the code, defaults
                           to 'detect', attempting to auto detect the type of
                           content
        """
        self.source = ''

        if filename:
            filename = os.path.abspath(filename)
            with open(filename) as f:
                self.source += f.read()

        if text:
            self.source += text

        self.source = self.source.rstrip('n')

        from purdy.parser import LEXERS
        if lexer_name == 'detect':
            self.lexer = LEXERS.detect_lexer(self.source)
        else:
            self.lexer = LEXERS.get_lexer(lexer_name)

# -----------------------------------------------------------------------------

class RenderHook:
    def line_appended(self, listing, line):
        pass

    def line_inserted(self, listing, position, line):
        pass

    def line_removed(self, listing, position):
        pass

    def line_changed(self, listing, position, line):
        pass

    def clear(self):
        pass


class Listing:
    """A container for a set of :class:`CodeLine` objects."""

    def __init__(self, code=None, starting_line_number=-1):
        """Constructor

        :param code: a :class:`Code` or list of :class:`Code` objects to
                     populate this display with
        :param starting_line_number: If a non-negative integer, this value is
                                     the starting value of line numbers
                                     displayed with the code. A value of -1,
                                     the default, turns line numbering off
        """
        self.starting_line_number = starting_line_number

        self.colourizer = COLOURIZERS['plain']
        self.render_hook = RenderHook()
        self.lines = []

        if code:
            if isinstance(code, Code):
                self.append_code(code)
            else:
                for item in code:
                    self.append_code(code)

    def set_display(self, mode='plain', render_hook=None):
        """Code can be displayed using a variety of methods, from colourized
        text to the urwid TUI client. This method sets the options to control
        how rendering is done.

        :param mode: a key from :attr:`purdy.colour.COLOURIZERS` indicating
                     which colourizer routine is used to coulour the source in
                     this box. Defaults to 'plain'.
        :param render_hook: an optional hook the box calls when actions are
                            done on the box. Used by the TUI client so that
                            when something changes in the it is reflected in
                            the TUI.
        """
        if mode:
            self.colourizer = COLOURIZERS[mode]

        if render_hook:
            self.render_hook = render_hook

    #--- Add/Remove Line Methods
    def append_code(self, code):
        """Parses contents of a :class:`Code` object and appends it to this
        box."""
        lines = parse_source(code.source, code.lexer)
        self.append_lines(lines)

    def append_lines(self, lines):
        new_lines = copy(lines)

        if self.starting_line_number != -1:
            num = self.starting_line_number + len(self.lines)
            for line in new_lines:
                line.line_number = num
                num += 1

        self.lines.extend(new_lines)
        for line in new_lines:
            self.render_hook.line_appended(self, line)

    def insert_lines(self, position, lines):
        # loop through lines and insert them, assigning a new line number if
        # needed
        new_lines = copy(lines)

        for count, line in enumerate(new_lines):
            if self.starting_line_number > -1:
                line.line_number = position + count + \
                    self.starting_line_number - 1

            self.lines.insert(count + position - 1, line)
            self.render_hook.line_inserted(self, position + count, line)

        if self.starting_line_number > -1:
            # reset line numbers after insertion: 
            #    => position + 1 + len(lines) - 1
            num = position + len(new_lines)
            self.reset_line_numbers(num)

    def replace_line(self, position, line):
        """Replaces the line at the given position with the given
        :class:`CodeLine` object"""
        new_line = copy(line)
        if self.starting_line_number != -1:
            new_line.line_number = position + self.starting_line_number - 1

        self.lines[position - 1] = new_line
        self.render_hook.line_changed(self, position, new_line)

    def remove_lines(self, position, size):
        for x in range(1, size + 1):
            del self.lines[position - 1]

            self.render_hook.line_removed(self, position)

        if self.starting_line_number > -1:
            self.reset_line_numbers(position)

    def clear(self):
        self.lines = []
        self.render_hook.clear()

    #--- Style Methods

    def set_highlight(self, highlight, start=1, end=-1):
        """Turns highlighting on for the lines of code

        :param highlight: boolean value, True for turning highlighting on
        :param start: line number to start highlighting on (1-indexed), 
                      defaults to 1 
        :param end: line number to highlight until, inclusive (1-indexed),
                    a value of -1 indicates to change the highlight from start
                    until the end of the list. Defaults to -1
        """
        first = start - 1
        last = end
        if end == -1:
            last = len(self.lines)

        for count, line in enumerate(self.lines[first:last]):
            index = start + count
            line.highlight = highlight
            self.render_hook.line_changed(self, index, line)

    def reset_line_numbers(self, position):
        """Reset the line numbers, starting at the given parameter

        :param position: positon to start fixing the line numbers at
        """
        for count, line in enumerate(self.lines[position - 1:]):
            current_position = position + count
            line.line_number = self.starting_line_number + current_position - 1
            self.render_hook.line_changed(self, current_position, line)

    #--- Export methods
    def content(self):
        """Returns a list of colourized strings. Uses the colourizer set with
        :funct:`Listing.set_display`.
        """
        result = []
        for line in self.lines:
            result.append( self.render_line(line) )

        return result

    def render_line(self, line):
        return line.render_line(self.colourizer)
