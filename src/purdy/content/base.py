# handlers/base.py
#
# Common classes for code content handlers
import math

from copy import deepcopy
from pathlib import Path

from purdy.parser import Parser, CodeLine, CodePart

# ===========================================================================

class _BaseCode:
    # Abstract base for code content handlers
    #
    # Expects a concrete implementation to provide an "output_line(index)"
    # method
    def __init__(self):
        self.wrap = None
        self.enable_line_numbers = False
        self.starting_line_number = 1
        self.highlighting = set()
        self.partial_highlighting = {}

        self.folds = []
        self.fold_set = set()

        self.lines = []  # Sub-class to fill this with content

    # --- Content iteration and access
    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self.output_line(x) for x in range(index.start, index.stop)]

        # Not a slice
        return self.output_line(index)

    # --- Folding
    def fold(self, index, length):
        """Create a fold in the code

        :param index: Index number to start the fold at
        :param length: how many lines to include in the fold
        """
        # self.folds is a list of tuples with the first part indicates the
        # beginning line number of the fold and the second part the number of
        # lines participating in the fold
        #
        # Error if a fold overlaps any existing ones
        for start, size in self.folds:
            if start <= index <= start + size:
                raise ValueError(
                    f"Index {index} is within fold {start}-{start+size}")

        # Add fold to list of folds
        self.folds.append( (index, length) )
        self.folds.sort()

        # Update the fold set for easy look-up
        self.fold_set = set()
        for start, size in self.folds:
            self.fold_set.update(range(start, start+size))

    def unfold(self, index):
        """Removes a previously created fold that starts on the given index
        line."""
        remove = None
        for count, fold in enumerate(self.folds):
            if fold[0] == index:
                remove = count
                break

        if remove is not None:
            del self.folds[remove]

        # Update the fold set for easy look-up
        self.fold_set = set()
        for start, size in self.folds:
            self.fold_set.update(range(start, start+size))

    def fold_count(self, index):
        """Gives information about the fold state of the given line.

        :param index: Index of line to process
        :return: None if the line is not folded, 1 if the it is the first line
            in a fold, and 2 if it is deeper in the fold
        """
        if index in self.fold_set:
            # The index is folded, check if it is the first in the fold
            for start, _ in self.folds:
                if index == start:
                    return 1

            # If you get here, then it wasn't the starting point in the fold
            return 2

        # Not folded
        return None

    # --- Wrapping
    def _chunk_line(self, compare, output):
        wrapped = CodeLine(spec=compare.spec, has_newline=True)
        length = 0

        for part_count, part in enumerate(compare.parts):
            length += len(part.text)
            if length > self.wrap:
                # Split the line at this point
                cut_at = self.wrap - length   # -ve, chars from right
                left_of = part.text[0:cut_at]
                split_point = left_of.rfind(" ")

                if split_point == -1:
                    # No split point in the text, move it all into the next
                    # line
                    output.append(wrapped)

                    next_line = CodeLine(spec=compare.spec, has_newline=True)
                    next_line.parts.extend(compare.parts[part_count:])
                    return next_line

                # Stuff everything to the left into the current line
                left = CodePart(part.token, part.text[:split_point + 1])
                wrapped.parts.append(left)
                output.append(wrapped)

                # Everything else goes into the next line
                next_line = CodeLine(spec=compare.spec, has_newline=True)

                right = CodePart(part.token, part.text[split_point + 1:])
                next_line.parts.append(right)
                next_line.parts.extend(compare.parts[part_count + 1:])
                return next_line
            else:
                # Not a split point, Copy the CodePart into the wrapped line
                full = CodePart(part.token, part.text)
                wrapped.parts.append(full)

        # Got through the for-loop without returning, whatever is left is less
        # than the wrap lenght
        output.append(compare)
        return None

    def wrap_line(self, index):
        """Split a line up into multiple parts based on the wrap length.

        :param index: Index of line to split
        :returns: Returns a list of :class:`CodeLine` objects based on
            splitting the given one at the index. If no wrap was needed the
            list will contain the original :class:`CodeLine`
        """
        line = self.lines[index]

        # If wrapping is off, or the line is shorter than the wrap
        if self.wrap is None or line.parts.text_length < self.wrap:
            return [line]

        # Perform wrapping
        #
        # When a line is split into more than two, the wrap of the second line
        # starts where the second line got split. Wrapping at 20 does not mean
        # wrapping every 20 characters, it means no more than 20 past the last
        # splitting point
        output = []
        compare = deepcopy(line)

        while(compare):
            compare = self._chunk_line(compare, output)

        # Match the newline state of the last line
        output[-1].has_newline = line.has_newline
        return output

    # --- Line Numbers
    def line_number(self, index):
        """Returns the line number for the given index

        :returns: Line number right justified and padded, or empty string if
            line numbers are not enabled.
        """
        if not self.enable_line_numbers:
            return ""

        max_line = len(self.lines) + self.starting_line_number
        width = int(math.log10(max_line) + 1)
        return f"{self.starting_line_number + index:{width}d} "

    def line_number_gap(self):
        """Returns a whitespace string the width of a line number, useful for
        when dealing with wrapping
        """
        if not self.enable_line_numbers:
            return ""

        # log10 + 1 = width; add another 1 for the gutter space
        max_line = len(self.lines) + self.starting_line_number
        return int(math.log10(max_line) + 2) * " "

    # --- Highlighting
    def _parse_partial_highlight(self, indicator):
        indicator = indicator.replace(" ", "")
        index, scope = indicator.split(":")
        start, length = scope.split(",")

        index = int(index)
        if index < 0:
            # Negative indexing
            index = len(self.lines) + index

        self.partial_highlighting[index] = (int(start), int(length))

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
                # Partial highlights are a special case
                self._parse_partial_highlight(arg)
                return

            # Argument is for a full line add it to the highlighting set
            match arg:
                case int(indicator):
                    if indicator < 0:
                        indicator = len(self.lines) + indicator

                    self.highlighting.add(indicator)
                case (start, length):
                    if start < 0:
                        start = len(self.lines) + start

                    self.highlighting.update(
                        [x for x in range(start, start + length)])
                case str(indicator):
                    indicator = indicator.strip()
                    start, length = indicator.split("-")
                    start = int(start)
                    self.highlighting.update(
                        [x for x in range(start, start + int(length))])

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

            # Argument is for a full line add it to the highlighting set
            match arg:
                case int(indicator):
                    if indicator < 0:
                        indicator = len(self.lines) + indicator

                    self.highlighting.remove(indicator)
                case (start, length):
                    if start < 0:
                        start = len(self.lines) + start

                    self.highlighting -= set(
                        [x for x in range(start, start + length)])
                case str(indicator):
                    indicator = indicator.strip()
                    start, length = indicator.split("-")
                    start = int(start)
                    self.highlighting -= set(
                        [x for x in range(start, start + int(length))])

    def highlight_all_off(self):
        """Removes all highlighting"""
        self.highlighting = set()
        self.partial_highlighting = {}


class _Code(_BaseCode):
    """Abstract base class for a content handler that reads code read in from
    a file.

    :param filename: Name of file to read of :class:`pathlib.Path` object
    :param parser_identifier: Identifier for :class:`purdy.parser.Parser` to
        use when parsing the code. Defaults to "detect"
    """
    def __init__(self, filename, parser_identifier="detect"):
        super().__init__()
        self.parser = Parser(parser_identifier, hint=filename)
        path = Path(filename).resolve()

        self.lines = self.parser.parse(path.read_text())


class _TextCode(_BaseCode):
    """Abstract base class for a content handler that reads code read in from
    a string.

    :param text: Text to parse
    :param parser_identifier: Identifier for :class:`purdy.parser.Parser` to
        use when parsing the code. Defaults to "py".
    """
    def __init__(self, text, parser_identifier="py"):
        super().__init__()
        self.parser = Parser(parser_identifier)
        self.lines = self.parser.parse(text)
