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
        self.highlighting = {}

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


class _Code(_BaseCode):
    """Content handler for code read in from a file.

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
    """Content handler for code read in from a string.

    :param text: Text to parse
    :param parser_identifier: Identifier for :class:`purdy.parser.Parser` to
        use when parsing the code. Defaults to "py".
    """
    def __init__(self, text, parser_identifier="py"):
        super().__init__()
        self.parser = Parser(parser_identifier)
        self.lines = self.parser.parse(text)
