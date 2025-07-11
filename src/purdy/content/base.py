# handlers/base.py
#
# Common classes for code content handlers
from pathlib import Path

from purdy.parser import Parser

# ===========================================================================

class _BaseCode:
    # Abstract base for code content handlers
    #
    # Expects a concrete implementation to provide an "output_line(index)"
    # method
    def __init__(self):
        self.wrap = False
        self.enable_line_numbers = False
        self.starting_line_number = 1
        self.line_number_size = 0
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

    # --- Handle folding
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
