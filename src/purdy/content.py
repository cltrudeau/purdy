# content.py
#
# Code encapsulation and stylization
import math

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

from purdy.parser import (Parser, CodeLine, CodePart, HighlightOn,
    HighlightOff, Fold, LineNumber)

# ===========================================================================
# Code Block
# ===========================================================================

class Code(list):
    """Encapsulates :class:`CodeLine` objects to track lines of code."""

    """Read code from a file, build an associated parser, and add the
    resulting lines to this object.

    :param filename: Name of file to read of :class:`pathlib.Path` object
    :param parser_identifier: Identifier for :class:`purdy.parser.Parser` to
        use when parsing the code. Defaults to "detect"
    """
    def __init__(self, filename, parser_identifier="detect"):
        # !!! If any defaults in here change make sure to update the .text()
        # factory
        super().__init__()
        self.parser = Parser(parser_identifier, hint=filename)
        path = Path(filename).resolve()

        self.parser.parse(path.read_text(), self)

    @classmethod
    def text(cls, text, parser_identifier="py"):
        """Factory method for reading code from a string instead of a file.

        :param text: Text to parse
        :param parser_identifier: Identifier for :class:`purdy.parser.Parser` to
            use when parsing the code. Defaults to "py".
        """
        # A bit tricky: construct the object without invoking __init__
        obj = Code.__new__(Code)
        obj.parser = Parser(parser_identifier)
        obj.parser.parse(text, obj)
        return obj

    def spawn(self):
        """Returns a new :class:`Code` object with the same parser as this
        one, but otherwise empty."""
        obj = Code.__new__(Code)
        obj.parser = self.parser
        return obj

# ===========================================================================
# Styling
# ===========================================================================

@dataclass
class _CodeLineMetadata:
    """Used to track data associated with a :class:`CodeLine` within a
    :class:`Stylizer`.
    """
    highlight: bool = False
    highlight_partial: list = field(default_factory=list)
    folded: bool = False
    hidden: bool = False


class Stylizer:
    def __init__(self, code):
        """Class represents styling applied to a :class:`Code` object.

        :param code: `Code` object containing lines of code to style
        """
        self.wrap = None
        self.line_numbers_enabled = False
        self.starting_line_number = 1
        self.line_number_gap_char = " "
        self.fold_char = "⠇"

        self.meta = defaultdict(_CodeLineMetadata)
        self.code = code

    def reset_metadata(self):
        """Empties out all metadata associated with this style. Mostly used
        for testing.
        """
        self.meta = defaultdict(_CodeLineMetadata)

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

    def apply_wrapping(self, line):
        """Split a line up into multiple parts based on the wrap length.

        :param line: :class:`CodeLine` to used to be split into wrapped lines

        :returns: Returns a list of :class:`CodeLine` objects based on
            splitting the given one. If no wrap was needed the list contain
            the original :class:`CodeLine`
        """
        compare = deepcopy(line)

        # If wrapping is off, or the line is shorter than the wrap
        if self.wrap is None or line.parts.text_length < self.wrap:
            return [compare]

        # Perform wrapping
        #
        # When a line is split into more than two, the wrap of the second line
        # starts where the second line got split. Wrapping at 20 does not mean
        # wrapping every 20 characters, it means no more than 20 past the last
        # splitting point
        result = []

        while(compare):
            compare = self._chunk_line(compare, result)

        # Match the newline state of the last line
        result[-1].has_newline = line.has_newline
        return result

    # --- Line Numbers
    def line_number(self, index):
        """Returns the line number for the given index

        :returns: Line number right justified and padded, or empty string if
            line numbers are not enabled.
        """
        if not self.line_numbers_enabled:
            return ""

        max_line = len(self.code) + self.starting_line_number
        width = int(math.log10(max_line) + 1)
        return f"{self.starting_line_number + index:{width}d} "

    def line_number_gap(self):
        """Returns a whitespace string the width of a line number, useful for
        when dealing with wrapping
        """
        if not self.line_numbers_enabled:
            return ""

        # log10 + 1 = width; add another 1 for the gutter space
        max_line = len(self.code) + self.starting_line_number
        return int(math.log10(max_line) + 2) * " "

    # --- Highlighting Application
    @classmethod
    def _expand_parts(cls, line):
        """Creates a new list of parts expanding the text of each part into
        its own :class:`CodePart`, essentially creating parts consisting of a
        single letter.

        :param line: :class:`CodeLine` to expand
        :returns: list of :class:`CodePart` objects
        """
        char_parts = []
        for part in line.parts:
            if len(part.text) == 0:
                char_parts.append(deepcopy(part))
                continue

            for char in part.text:
                char_parts.append(CodePart(part.token, char))

        return char_parts

    @classmethod
    def _chop_partial_highlight(cls, line, cutpoints):
        """Creates a new CodeLine with highlight tokens at partial highlight
        spots

        :param line: CodeLine to copy and transform
        :param cutpoints: iterable of (start, length) cut point tuples
        """
        cutpoints.sort()
        char_parts = cls._expand_parts(line)

        # Loop through our single-character listing and insert the appropriate
        # highlight on and off tokens
        char_count = 0
        start = cutpoints[0][0]   # start char for first marker
        end = cutpoints[0][0] + cutpoints[0][1]  - 1 # end char for first marker
        cut_index = 0
        output = CodeLine(line.spec, has_newline=line.has_newline)
        highlighting = False
        for part in char_parts:
            if char_count == start and len(part.text) != 0 and not highlighting:
                output.parts.append(CodePart(HighlightOn, ""))
                output.parts.append(part)
                char_count += 1
                highlighting = True
                continue

            if char_count == end and len(part.text) != 0 and highlighting:
                char_count += 1
                output.parts.append(part)
                output.parts.append(CodePart(HighlightOff, ""))
                highlighting = False
                try:
                    # Was ended, advance to next cutpoint
                    cut_index += 1
                    start = cutpoints[cut_index][0]
                    end = cutpoints[cut_index][0] + cutpoints[0][1] - 1

                except IndexError:
                    # No cutpoints left, do nothing
                    pass

                continue

            output.parts.append(part)
            char_count += len(part.text)

        # Recompress our output
        output.compress()
        return output

    def apply_highlight(self, index):
        """Creates a new :class:`CodeLine` as a copy of the given one but
        with highlight tokens applied.

        :param index: Index value of `CodeLine` to highlight
        """
        output = deepcopy(self.code[index])
        if index in self.meta and self.meta[index].highlight:
            output.parts.insert(0, CodePart(HighlightOn, ""))
            output.parts.append(CodePart(HighlightOff, ""))
        elif index in self.meta and self.meta[index].highlight_partial:
            # Split the line up as needed for partial highlighting
            output = self._chop_partial_highlight(output,
                self.meta[index].highlight_partial)

        # Else: no highlighting
        return output

    # --- Highlight Setters
    def _set_highlight(self, indicator, value):
        match indicator:
            case int(index):
                if index < 0:
                    index = len(self.code) + index

                self.meta[index].highlight = value
            case (start, length):
                if start < 0:
                    start = len(self.code) + start

                for index in range(start, start + length):
                    self.meta[index].highlight = value
            case str(indicator):
                indicator = indicator.strip()
                start, stop = indicator.split("-")

                for index in range(int(start), int(stop) + 1):
                    self.meta[index].highlight = value

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
                    index = len(self.code) + index

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
        for i in range(index + 1, len(self.code)):
            if i not in self.meta or not self.meta[i].hidden:
                break

            self.meta[i].hidden = False

    # --- Apply Style
    def apply(self, transform_fn, *args, **kwargs):
        """Process our :class:`Code` object and apply transformations based on
        the state of the class, like line numbers, highlighting, etc.

        :param transform_fn: a renderer function that converts the token
            representation to a string one.
        :param args: [Optional] arguments to pass to the renderer function
        :param kwargs: [Optional] keyword arguments to pass to the renderer
            function

        :returns: String representation of code with style applied
        """
        code_copy = self.code.spawn()
        for index, line in enumerate(self.code):
            if index in self.meta and self.meta[index].hidden:
                continue

            if index in self.meta and self.meta[index].folded:
                # This is the parent line in a fold, display an indicator
                # instead
                output = CodeLine(spec=line.spec, has_newline=True)
                output.parts.append(CodePart(Fold, text=self.fold_char))

                if self.line_numbers_enabled:
                    line_no = self.line_number(index)
                    part = CodePart(LineNumber, line_no)
                    output.parts.insert(0, part)

                code_copy.append(output)
                continue

            # Handle highlighting and wrapping
            output = self.apply_highlight(index)
            wrapped = self.apply_wrapping(output)

            if self.line_numbers_enabled:
                # Apply line numbers to first wrapped line
                line_no = self.line_number(index)
                part = CodePart(LineNumber, line_no)
                wrapped[0].parts.insert(0, part)

                for piece in wrapped[1:]:
                    gap = self.line_number_gap()
                    part = CodePart(LineNumber, gap)
                    piece.parts.insert(0, part)

            for piece in wrapped:
                code_copy.append(piece)

        # Now that the decoration tokens have been applied, use the provided
        # transformation function to create the text
        text = transform_fn(code_copy, *args, **kwargs)
        return text
