# content.py
#
# Encapsulates a block of code and manages any associated style information
import math

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

from purdy.parser import LexerSpec, Parser
from purdy.themes import THEME_MAP

# ===========================================================================

@dataclass
class _CodeLineMetadata:
    ### Used to track data associated with a :class:`CodeLine` within a
    # :class:`Motif`.
    highlight: bool = False
    highlight_partial: list = field(default_factory=list)
    folded: bool = False
    hidden: bool = False


class Code:
    """Encapsulates :class:`CodeLine` objects to track lines of code and any
    associated style information."""

    """Read code from a file, build an associated parser, and add the
    resulting lines to this object.

    :param filename: Name of file to read of :class:`pathlib.Path` object
    :param parser_identifier: Identifier for :class:`purdy.parser.Parser` to
        use when parsing the code. Defaults to "detect"
    :param theme: Either a string containing the base name of a theme (without
        the category type like code, con, etc) or a :class:Theme object.
        Defaults to `None` in which case it uses the class attribute
        `default_theme_name` as the theme name.
    """
    default_theme_name = "default"

    def __init__(self, filename, parser_identifier="detect", theme=None):
        # !!! If any defaults in here change make sure to update the .text()
        # factory
        lexer_spec = LexerSpec.get_spec(parser_identifier, hint=filename)
        self._pre_parse_init(theme, lexer_spec)

        path = Path(filename).resolve()
        self.parser = Parser(lexer_spec)
        self.parser.parse(path.read_text(), self)

        # !!! Anything added under here has to be copied to the text factory
        # and the spawn methods!!!

    @classmethod
    def text(cls, text, parser_identifier="py", theme=None):
        """Factory method for reading code from a string instead of a file.

        :param text: Text to parse
        :param parser_identifier: Identifier for :class:`purdy.parser.Parser` to
            use when parsing the code. Defaults to "py".
        """
        # A bit tricky: construct the object without invoking __init__
        obj = Code.__new__(Code)

        lexer_spec = LexerSpec.get_spec(parser_identifier)
        obj._pre_parse_init(theme, lexer_spec)

        obj.parser = Parser(lexer_spec)
        obj.parser.parse(text, obj)

        # !!! Anything added under here has to match __init__ and spawn!
        return obj

    def _pre_parse_init(self, theme, lexer_spec):
        ### Since the `.text` method does tricky stuff with `__new__`, common
        # initialization is done in this method
        self.lines = []
        self.current = 0

        self.meta = defaultdict(_CodeLineMetadata)

        if theme is None:
            theme = self.default_theme_name

        if isinstance(theme, str):
            self.theme = THEME_MAP[theme][lexer_spec.category]
        else:
            self.theme = theme

    def reset_metadata(self):
        """Sets all the style metadata back to defaults. Mostly used for
        testing.
        """
        self.meta = defaultdict(_CodeLineMetadata)

    # --- Accessors
    def __getitem__(self, index):
        """Returns a new `Code` object containing the subset of `CodeLine`
        objects indicated by `index`

        :param index: an integer or a slice
        :returns: A copy of this `Code` object but containing only a subset of
            ts lines
        """
        code = self.spawn()
        if isinstance(index, slice):
            code.lines = deepcopy(self.lines[index.start:index.stop])
        else:
            code.lines = deepcopy(self.lines[index])

        return code

    def spawn(self):
        """Returns a new :class:`Code` object with the same parser and theme
        as this one, but empty of any code lines."""
        obj = Code.__new__(Code)
        obj.lines = []
        obj.parser = self.parser
        obj.current = 0
        obj.meta = defaultdict(_CodeLineMetadata)
        obj.theme = self.theme

        return obj

    def chunk(self, amount):
        """This method is for doing iterator-like access to the `Code` object.
        Each call returns a copy of the object containing a subset of lines,
        with each subsequent call returning the next subset. To reset to the
        beginning, set :attr:`Code.current` to 0.

        :param amount: Number of `CodeLine` objects to  include in the
            result
        :returns: A copy of this `Code` object but containing only a subset of
            ts lines
        """
        code = self[self.current:self.current + amount]
        self.current += amount
        return code

    def remaining_chunk(self):
        """Associated with the :method:`Code.chunk` call, but returns whatever
        is left in the block.

        :returns: A copy of this `Code` object but containing the lines
            remaining in the chunkification process
        """
        code = self[self.current:]
        self.current = len(self.lines)
        return code

    # === Style Methods

    # --- Fold Management
    def fold(self, index, length):
        """Create a fold in the code

        :param index: Index number to start the fold at
        :param length: how many lines to include in the fold
        """
        # Nested folding is not supported, check for overlaps and error out
        for i in range(index, index + length):
            if i in self.meta and (self.meta[i].folded or self.meta[i].hidden):
                raise ValueError("Nested folding is not allowed")

        # Fold the line
        self.meta[index].folded = True
        for i in range(index + 1, index + length):
            self.meta[i].hidden = True

    def unfold(self, index):
        """Removes a previously created fold that starts on the given index
        line."""
        if index not in self.meta or (not self.meta[index].folded):
            raise ValueError(f"Line {index} was not the beginning of a fold")

        self.meta[index].folded = False

        # Loop through everything past the fold and unhide if hidden
        for i in range(index + 1, len(self.lines)):
            if i not in self.meta or not self.meta[i].hidden:
                break

            self.meta[i].hidden = False

    # --- Highlight Setters
    def _set_highlight(self, indicator, value):
        match indicator:
            case int(index):
                if index < 0:
                    index = len(self.lines) + index

                self.meta[index].highlight = value
            case (start, length):
                if start < 0:
                    start = len(self.lines) + start

                for index in range(start, start + length):
                    self.meta[index].highlight = value
            case str(indicator):
                indicator = indicator.strip()
                if indicator.startswith("-"):
                    # Negative Number
                    index = len(self.lines) + int(indicator)

                    self.meta[index].highlight = value
                elif "-" in indicator:
                    # Range
                    start, stop = indicator.split("-")

                    for index in range(int(start), int(stop) + 1):
                        self.meta[index].highlight = value
                else:
                    # Positive number
                    self.meta[int(indicator)].highlight = value

    def highlight(self, *args):
        """Turn highlighting on for one or more code lines. Each argument can
        be an int (index value, supports negative indexing), a tuple
        (specifying starting line and number of lines to highlight, start line
        can be negative), a string specifying a range ("1-3" highlights lines
        1 through 3 inclusive), or a partial highlight.

        Partial highlights support highlighting a subset of a line and are
        specified by a line number, a colon, a startng character position and
        a length.  Example "3:15,5" highlights characters 15-20 on index line
        3. The line number indicator supports negative indexing.

        All start positions are zero indexed.
        """
        for arg in args:
            if isinstance(arg, str) and ":" in arg:
                arg = arg.replace(" ", "")
                index, scope = arg.split(":")
                start, length = scope.split(",")

                index = int(index)
                if index < 0:
                    # Negative indexing
                    index = len(self.lines) + index

                self.meta[index].highlight_partial.append( (int(start),
                    int(length)) )
                continue

            # Argument is for a full line add it to the highlighting set
            self._set_highlight(arg, True)

    def highlight_off(self, *args):
        """Turns highlighting for one or more code lines. Each argument can be
        an int line index (negative indexing supported), a tuple (start
        indexing and number of lines to turn off) or a string specifying a range
        ("3-5" turns off line indexes 3 through 5).

        This turns off highlighting for both full lines and partial
        highlights. There is no way of turning off just a single partial
        inside of a line, if this is needed, turn off the line and turn
        partial back on for any segments you wish to keep.

        Turning off a line that is not highlighted is ignored.
        """
        for arg in args:
            if isinstance(arg, str) and ":" in arg:
                raise ValueError("Partials not supported. Turn off full line")

            # Argument is for one or more full lines, turn them off
            self._set_highlight(arg, False)

    def highlight_all_off(self):
        """Removes all highlighting"""
        for value in self.meta.values():
            value.highlight = False
            value.highlight_partial = defaultdict(list)

# ===========================================================================

class MultiCode(list):
    """Container for multiple :class:`Code` objects. Constructor optionally
    takes a `Code` object or iterable of `Code` objects to initialize the set"""
    def __init__(self, contents=None):
        if isinstance(contents, Code):
            super().__init__([contents])
        elif contents is not None:
            super().__init__(contents)
        else:
            super().__init__()

        self.background = None
        self.line_numbers_enabled = False
        self.starting_line_number = 1
        self.line_number_gap_char = " "
        self.wrap = None
        self.fold_char = "⠇"

    def extend(self, code):
        """Adds a new :class:`Code` object to this container

        :param code: a `Code` object to add to the container
        """
        self.append(code)

    # --- Line Numbers
    def line_number(self, code_index, line_index):
        """Returns the line number for the given indexes

        :param code_index: index of :class:`Code` in this container
        :param line_index: index of the :class:`CodeLine` within the `Code`
            object

        :returns: Line number right justified and padded, or empty string if
            line numbers are not enabled.
        """
        if not self.line_numbers_enabled:
            return ""

        # Calculate the spacing
        max_line = self.starting_line_number
        for code in self:
            max_line += len(code.lines)

        # log10 + 1 = width; add another 1 for the gutter space
        width = int(math.log10(max_line) + 1)

        # Calculate the line number
        line_number = self.starting_line_number
        for code in self[:code_index]:
            line_number += len(code.lines)

        line_number += line_index

        return f"{line_number:{width}d} "

    def line_number_gap(self):
        """Returns a whitespace string the width of a line number, useful for
        when dealing with wrapping
        """
        if not self.line_numbers_enabled:
            return ""

        max_line = self.starting_line_number
        for code in self:
            max_line += len(code.lines)

        # log10 + 1 = width; add another 1 for the gutter space
        return int(math.log10(max_line) + 2) * " "
