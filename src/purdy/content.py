"""
Content
=======

Reperesntations of source code are found in this module.
"""
from copy import deepcopy
from math import log10
from pathlib import Path

from pygments.token import Generic

from purdy.parser import (CodeLine, CodePart, Parser, LineNumber, HighlightOn,
    HighlightOff)
from purdy.utils import string_length_split

#import logging
#logging.basicConfig(filename='debug.log', level=logging.DEBUG)
#logger = logging.getLogger()

# =============================================================================

class Code:
    """Represents source code from the user as a series of lines. Each line is
    made up of one or more :class:`purdy.parsers.CodePart` object that holds
    the token type and corresponding text.

    :param filename: name of a file to read for content. If both this and
                     `text` is given, `filename` is used first. Can also be a
                     `pathlib.Path` object

    :param text: a string containing code

    :param parser: either the name of a parser or a
                  :class:`purdy.parser.Parser` class responsible for
                  turning the source into tokens. Defaults to "detect" which
                  attempts to auto-detect the parser based on the filename

    :param filters: one or more filters to apply to the source before parsing
    """

    def __init__(self, filename='', text='', parser='detect', filters=[]):
        self.source = ''
        self.current_line = 0

        if filename:
            if isinstance(filename, str):
                filename = Path(filename)

            self.source += filename.read_text()

        if text:
            self.source += text

        if parser == 'detect':
            if filename == '':
                raise AttributeError("Can only use parser=='detect' with files")

            try:
                self.parser = Parser.from_name(filename.suffix[1:])
            except AttributeError:
                raise AttributeError("No parser registered for "
                    f"{filename.suffix}")
        elif isinstance(parser, str):
            try:
                self.parser = Parser.from_name(parser)
            except AttributeError:
                raise AttributeError(f"No parser called {parser}")
        else:
            self.parser = parser

        for filtrate in filters:
            if isinstance(filtrate, type):
                filtrate = filtrate()

            self.source = filtrate.filter(self.source)

        # Parse the code into a series of parser.CodeLine objects
        self.lines = self.parser.parse(self.source)

    def clone(self, filters=[]):
        return Code(text=self.source, parser=self.parser, filters=filters)

    # -----
    # Access mechanisms
    def _iterate(self, start, end):
        for index in range(start, end):
            yield self.lines[index]

    def __iter__(self):
        return self._iterate(0, len(self.lines))

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._iterate(index.start, index.stop)
        else:
            return self.lines[index]

    def chunk(self, amount):
        start = self.current_line
        end = start + amount
        self.current_line = end
        if end > len(self.lines):
            end = len(self.lines)

        return self._iterate(start, end)

# -----------------------------------------------------------------------------

class _ListingLine(CodeLine):
    padded_num = lambda n, w: f'{n:{w}} '

    def __init__(self, code_line=None, line_number=None, line_number_width=0):
        self.length = 0
        self.parts = []
        self.line_number = line_number
        self.line_number_width = line_number_width

        if code_line:
            self.spec = code_line.spec

            if line_number is not None:
                self.parts.append(CodePart(LineNumber, self.padded_num))
                self.length += len(num)

            for part in code_line.parts:
                self.length += len(part.text)
                self.parts.append(deepcopy(part))

    @property
    def padded_num(self):
        return f'{self.line_number:{self.line_number_width}} '


    def set_line_number(self, line_number, line_number_width):
        """Sets the line number for this line. If `line_number` is `None`, any
        existing line number is removed.

        :param line_number: new number for this line (int)
        :param line_number_width: width of padding for the number

        :returns: next line number after this one, or `None` if was set to
            `None`
        """
        self.line_number = line_number

        # Removing the line number
        if line_number is None:
            self.line_number_width = 0
            if self.parts[0].token == LineNumber:
                self.parts = self.parts[1:]

            return None

        # Adding or changing the line number
        delta = line_number_width - self.line_number_width
        self.line_number_width = line_number_width

        if self.parts[0].token == LineNumber:
            self.parts[0].text = self.padded_num
        else:
            self.parts.insert(0, CodePart(LineNumber, self.padded_num))

        self.length += delta

        return line_number + 1

    # ----
    # Highlighting

    def highlight(self):
        pos = 0
        if self.parts[0].token == LineNumber:
            pos = 1

        self.parts.insert(pos, CodePart(HighlightOn, ''))
        self.parts.append(CodePart(HighlightOff, ''))

    def highlight_fractional(self, start, end):
        pos = 0
        highlighting = False
        change = []

        for part in self.parts:
            if part.token == LineNumber:
                change.append( deepcopy(part) )
                continue

            if len(part.text) + pos < start:
                # Before highlighting
                change.append( deepcopy(part) )
            elif start <= pos <= end:
                # Inside highlighting
                if not highlighting:
                    # Start the highlight
                    change.append( CodePart(HighlightOn, '') )
                    highlighting = True

                if len(part.text) + pos < end:
                    # Whole thing gets highlighted, just add it
                    change.append( deepcopy(part) )
                else:
                    # Need to split inside the part
                    split_point = end - pos + 1
                    left = part.text[0:split_point]
                    right = part.text[split_point:]

                    change.append( CodePart(part.token, left) )
                    change.append( CodePart(HighlightOff, '') )
                    change.append( CodePart(part.token, right) )
                    highlighting = False
            else:
                # After highlighting
                change.append( deepcopy(part) )

            pos += len(part.text)

        self.parts = change

    def highlight_off(self):
        change = []
        for part in self.parts:
            if part.token == HighlightOn or part.token == HighlightOff:
                continue

            change.append( deepcopy(part) )

        self.parts = change

    # ---
    # Wrap Management
    def wrap_at_length(self, size):
        """Processes the current line for a maximum width, returning a list of
        part lists each limited to the given size
        """

        if self.length < size:
            return [self.parts]

        pieces = []
        piece_length = 0
        current_piece = []

        for part in self.parts:
            if len(part.text) + piece_length < size:
                current_piece.append(part)
                piece_length += len(part.text)
                continue

            # Hit a splitting point
            split_point = size - piece_length
            left = part.text[0:split_point]
            right = part.text[split_point:]

            # Add the left chunk to the current piece
            current_piece.append( CodePart(part.token, left) )
            pieces.append(current_piece)
            current_piece = []
            piece_length = 0

            sections = string_length_split(right, size)
            for section in sections:
                current_piece.append( CodePart(part.token, section) )
                pieces.append(current_piece)
                current_piece = []

        return pieces


class Listing:
    """A container mapped to display a series of tokenized lines."""

    def __init__(self, code=None, starting_line_number=None):
        self._starting_line_number = starting_line_number
        self._old_starting_line_number = starting_line_number
        self.change_stamp = 0

        self.lines = []

        if code:
            for line in code.lines:
                self.lines.append(_ListingLine(line))

        self.recalculate_line_numbers()

    # -----
    # Access mechanisms
    def _iterate(self, start, end):
        for index in range(start, end):
                yield self.lines[index]

    def __iter__(self):
        return self._iterate(0, len(self.lines))

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._iterate(index.start, index.stop)
        else:
            return self.lines[index]

    # -----
    # Properties

    @property
    def starting_line_number(self):
        return self._starting_line_number

    @starting_line_number.setter
    def starting_line_number(self, new_value):
        self._starting_line_number = new_value
        self.recalculate_line_numbers()

    # -----
    # Line number management
    def toggle_line_numbers(self):
        if self.lines[0].parts[0].token == LineNumber:
            # Turn line numbers off
            self._old_starting_line_number = self.starting_line_number
            self.starting_line_number = None
        else:
            if self._old_starting_line_number is None:
                self._old_starting_line_number = 1

            self.starting_line_number = self._old_starting_line_number

    def recalculate_line_numbers(self):
        if self.starting_line_number is None:
            num = None
            width = 0
        else:
            num = self.starting_line_number
            largest = num + len(self.lines)
            width = int(log10(largest)) + 1

        for line in self.lines:
            num = line.set_line_number(num, width)

    # -----
    # Highlight management

    def highlight_off_all(self):
        """Turns off all highlighting in the listing"""
        self.change_stamp += 1
        for line in self.lines:
            line.highlight_off()

    def highlight_off(self, *args):
        """Turns off highlighting for one or more lines. Each argument is a
        highlight range indicator. Indicators can be:

        * int: the line number to turn off
        * tuple: the line number range (inclusive) to turn off

        All indicators are 1-indexed. Integer values support negative indexing
        """
        self.change_stamp += 1

        for value in args:
            if isinstance(value, int):
                if value > 0:
                    value -= 1

                self.lines[value].highlight_off()
            elif isinstance(value, tuple):
                for num in range(value[0], value[1] + 1):
                    self.lines[num - 1].highlight_off()

    def highlight(self, *args):
        """Turns on highlighting for one or more lines. Each argument is a
        highlight range indicator. Indicators can be:

        * int: the line number in the listing to highlight
        * tuple: the line number range in the listing to highlight, starting
                 from the first value and stopping at the second (inclusive)
        * string: handles several kinds of indicators

        String indicators can contain:

        * number: an int, for ease of use with command line parser, handles
                  the same was as int argument
        * range: two integers separated by a hyphen, handled the same as a
                 tuple above
        * fractional: support for specifying highlighting part of a line.
                      Specified as a line number, a period, then an optional
                      hyphenated range. For example "3.2-5" highlights
                      character 2 through 5 on line 3

        All indicators are 1-indexed. Negative indexes supported for single
        numbers and fractional use case, uses same semantics as Python with -1
        being the last line, which is weird mixed with 1-indexing, but hey,
        why not?

        """
        self.change_stamp += 1

        for value in args:
            if isinstance(value, int):
                if value > 0:
                    # 1-indexed for positive numbers
                    value -= 1

                self.lines[value].highlight()
            elif isinstance(value, tuple):
                if value[0] < 0:
                    raise ValueError("Negative indexing not supported")

                for num in range(value[0], value[1] + 1):
                    self.lines[num - 1].highlight()
            else:
                # Must be a string
                is_positive = True
                if value[0] == '-':
                    # Negative indexing case
                    is_positive = False
                    value = value[1:]

                if '-' not in value:
                    # Single number case, not a range
                    value = int(value)
                    if is_positive:
                        # 1-indexed for positive numbers
                        value -= 1
                    else:
                        # Put the negative back in it
                        value = 0 - value

                    self.lines[value].highlight()
                else:
                    # Ranged case, possibly fractional
                    left, right = value.split('-')
                    if '.' in left:
                        # Ranged, fractional highlight
                        line_num, start = left.split('.')

                        line_num = int(line_num)
                        if is_positive:
                            # 1-indexed line value
                            line_num -= 1
                        else:
                            # Put the negative back in it
                            line_num = 0 - line_num

                        self.lines[line_num].highlight_fractional(
                            int(start) - 1, int(right) - 1)
                    else:
                        # Ranged highlight with integers
                        left = int(left)
                        if not is_positive:
                            raise ValueError("Negative indexing not supported"
                                " with tuples")

                        right = int(right)
                        for num in range(left, right + 1):
                            self.lines[num - 1].highlight()

    # -----
    # Container operations

    def append(self, code):
        self.change_stamp += 1

        for line in code.lines:
            self.lines.append(_ListingLine(line))

        self.recalculate_line_numbers()
