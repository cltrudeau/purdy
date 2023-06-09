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

class Listing:
    """A container mapped to display a series of tokenized lines."""

    def __init__(self, code=None, starting_line_number=None):
        self._starting_line_number = starting_line_number
        self.change_stamp = 0

        self.lines = []

        if code:
            self.lines += deepcopy(code.lines)

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

    def recalculate_line_numbers(self):
        if self.starting_line_number is None:
            # Remove any existing line numbers
            for line in self.lines:
                first = line.parts[0]
                if first.token == LineNumber:
                    del line.parts[0]

            return

        # Find the amount of space needed for line numbers plus a margin
        # character
        largest = self.starting_line_number + len(self.lines)
        width = int(log10(largest)) + 1

        # Loop through and add the new line numbers
        for count, line in enumerate(self.lines):
            num = count + self._starting_line_number
            text = f'{num:{width}} '

            first = line.parts[0]
            if first.token == LineNumber:
                first.text = text
            else:
                line.parts.insert(0, CodePart(LineNumber, text))

    # -----
    # Highlight management

    def _highlight_line(self, index):
        line = self.lines[index]
        all_parts = iter(line.parts)

        if line.parts[0].token == LineNumber:
            parts = [deepcopy(line.parts[0]), CodePart(HighlightOn, '')]
            change = CodeLine(line.spec, parts)
            next(all_parts)
        else:
            change = CodeLine(line.spec, [CodePart(HighlightOn, '')])

        for part in all_parts:
            change.parts.append( deepcopy(part) )

        change.parts.append( CodePart(HighlightOff, '') )
        self.lines[index] = change

    def _highlight_fractional(self, index, start, end):
        line = self.lines[index]
        change = CodeLine(line.spec, [])

        pos = 0
        highlighting = False
        for part in line.parts:
            if part.token == LineNumber:
                change.parts.append( deepcopy(part) )
                continue

            if len(part.text) + pos < start:
                # Before highlighting
                change.parts.append( deepcopy(part) )
            elif start <= pos <= end:
                # Inside highlighting
                if not highlighting:
                    # Start the highlight
                    change.parts.append( CodePart(HighlightOn, '') )
                    highlighting = True

                if len(part.text) + pos < end:
                    # Whole thing gets highlighted, just add it
                    change.parts.append( deepcopy(part) )
                else:
                    # Need to split inside the part
                    split_point = end - pos + 1
                    left = part.text[0:split_point]
                    right = part.text[split_point:]

                    change.parts.append( CodePart(part.token, left) )
                    change.parts.append( CodePart(HighlightOff, '') )
                    change.parts.append( CodePart(part.token, right) )
                    highlighting = False
            else:
                # After highlighting
                change.parts.append( deepcopy(part) )

            pos += len(part.text)

        self.lines[index] = change

    def _highlight_line_off(self, index):
        line = self.lines[index]
        change = CodeLine(line.spec, [])
        for part in line.parts:
            if part.token == HighlightOn or part.token == HighlightOff:
                continue

            change.parts.append( deepcopy(part) )

        self.lines[index] = change

    def highlight_off_all(self):
        """Turns off all highlighting in the listing"""
        for index in range(0, len(self.lines)):
            self._highlight_line_off(index)

    def highlight_off(self, *args):
        """Turns off highlighting for one or more lines. Each argument is a
        highlight range indicator. Indicators can be:

        * int: the line number to turn off
        * tuple: the line number range (inclusive) to turn off

        All indicators are 1-indexed. Integer values support negative indexing
        """
        for value in args:
            if isinstance(value, int):
                if value > 0:
                    value -= 1

                self._highlight_line_off(value)
            elif isinstance(value, tuple):
                for num in range(value[0], value[1] + 1):
                    self._highlight_line_off(num - 1)

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
        for value in args:
            if isinstance(value, int):
                if value > 0:
                    # 1-indexed for positive numbers
                    value -= 1

                self._highlight_line(value)
            elif isinstance(value, tuple):
                if value[0] < 0:
                    raise ValueError("Negative indexing not supported")

                for num in range(value[0], value[1] + 1):
                    self._highlight_line(num - 1)
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

                    self._highlight_line(value)
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

                        self._highlight_fractional(line_num,
                            int(start) - 1, int(right) - 1)
                    else:
                        # Ranged highlight with integers
                        left = int(left)
                        if not is_positive:
                            raise ValueError("Negative indexing not supported"
                                " with tuples")

                        right = int(right)
                        for num in range(left, right + 1):
                            self._highlight_line(num - 1)

    # -----
    # Container operations

    def append(self, *args):
        """Adds lines to the listing. Accepts:

            * A string which it treats as generic output
            * A :class:`purdy.parser.CodeLine` object
            * A :class:`purdy.parser.Code` object

        Accepts multiple arguments, appending each in order
        """
        self.change_stamp += 1
        for item in args:
            if isinstance(item, str):
                # Passed a bare string, use the 'none' parser and general
                # output
                spec = Parser.registry['plain']
                line = CodeLine(spec, [CodePart(Generic.Output, item)])
                self.lines.append(line)
            elif isinstance(item, CodeLine):
                self.lines.append(item)
            elif isinstance(item, Code):
                self.lines += deepcopy(item.lines)
            else:
                raise ValueError("Unrecognized value to append: ", item)

        self.recalculate_line_numbers()
