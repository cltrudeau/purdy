# content.py
#
# Encapsulates a block of code and manages any associated style information
import math

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

from purdy.parser import (CodeLine, CodePart, Fold, HighlightOff, HighlightOn,
    LexerSpec, LineNumber, Parser)
from purdy.themes import THEME_MAP, EMPTY_THEME

# ===========================================================================

class Section:
    """Abstract base class for classes that contain a list of lines which can
    be collected inside of a class:`Document`"""
    def render(self, render_state):
        for line_index, line in enumerate(self.lines):
            self.render_line(render_state, line, line_index)

    def render_line(self, render_state, line, line_index):
        raise NotImplementedError()

# ===========================================================================

@dataclass
class _CodeLineMetadata:
    ### Used to track data associated with a :class:`CodeLine` within a
    # :class:`Motif`.
    highlight: bool = False
    highlight_partial: list = field(default_factory=list)
    folded: bool = False
    hidden: bool = False


class Code(Section):
    """Encapsulates :class:`~purdy.parser.CodeLine` objects to track lines of
    code and any associated style information.

    Constructor reads code from a file, build an associated parser, and add
    the resulting lines to this object.

    :param filename: Name of file to read of `pathlib.Path` object
    :param lexer: Identifier that determines which
        :class:`~purdy.parser.LexerSpec` to use when parsing the code. Defaults
        to "detect"
    :param theme: Either a string containing the base name of a theme (without
        the category type like code, con, etc) or a
        :class:`~purdy.themes.Theme` object.  Defaults to `None` in which case
        it uses the class attribute `default_theme_name` as the theme name.
    """
    default_theme_name = "default"

    def __init__(self, filename, lexer="detect", theme=None):
        # !!! If any defaults in here change make sure to update the .text()
        # factory
        lexer_spec = LexerSpec.get_spec(lexer, hint=filename)
        self._pre_parse_init(theme, lexer_spec)

        path = Path(filename).resolve()
        self.parser = Parser(lexer_spec)
        self.parser.parse(path.read_text(), self)

        # !!! Anything added under here has to be copied to the text factory
        # and the spawn methods!!!

    @classmethod
    def text(cls, text, lexer="py", theme=None):
        """Factory method for reading code from a string instead of a file.

        :param text: Text to parse
        :param lexer: Identifier that determines which
            :class:`~purdy.parser.LexerSpec` to use when parsing the code.
            Defaults to "detect"
        """
        # A bit tricky: construct the object without invoking __init__
        obj = Code.__new__(Code)

        lexer_spec = LexerSpec.get_spec(lexer)
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
        """Returns a new :class:`Code` object containing the subset of
        :class:`~purdy.parser.CodeLine` objects indicated by `index`

        :param index: an integer or a slice

        :returns: A copy of this :class:`Code` object but containing only a
            subset of ts lines
        """
        code = self.spawn()
        if isinstance(index, slice):
            code.lines = deepcopy(self.lines[index.start:index.stop])
        else:
            code.lines = [deepcopy(self.lines[index])]

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
        """This method is for doing iterator-like access to the :class:`Code`
        object.  Each call returns a copy of the object containing a subset of
        lines, with each subsequent call returning the next subset. To reset
        to the beginning, set `Code.current` to 0.

        :param amount: Number of :class:`~purdy.parser.CodeLine` objects to
            include in the result
        :returns: A copy of this :class:`Code` object but containing only a
            subset of its lines
        """
        code = self[self.current:self.current + amount]
        self.current += amount
        return code

    def remaining_chunk(self):
        """Associated with the :func:`Code.chunk` call, but returns whatever
        is left in the block.

        :returns: A copy of this :class:`Code` object but containing the lines
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
                # Single number, highlight full line
                if index < 0:
                    index = len(self.lines) + index

                self.meta[index].highlight = value
            case (start, length):
                # Tuple, highlight start and length following lines
                if start < 0:
                    start = len(self.lines) + start

                for index in range(start, start + length):
                    self.meta[index].highlight = value
            case str(indicator):
                # String can be an integer, or a range
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

    def _parse_partial(self, indicator):
        indicator = indicator.replace(" ", "")
        index, scope = indicator.split(":")
        start, length = scope.split(",")

        # Meta storage is a dictionary so need to turn the negative index into
        # its positive equivalent as the dict doesn't know -1 is the last item
        # in the list
        index = int(index)
        if index < 0:
            # Negative indexing
            index = len(self.lines) + index

        return index, (int(start), int(length))

    def highlight(self, *args):
        """Turn highlighting on for one or more code lines. Each argument can
        be an int (index value, supports negative indexing), a tuple
        (specifying starting line and number of lines to highlight, start line
        can be negative), a string specifying a range ("1-3" highlights lines
        1 through 3 inclusive), or a partial highlight.

        Partial highlights support highlighting a subset of a line and are
        specified by a line number, a colon, a starting character position and
        a length.  Example "3:15,5" highlights characters 15-20 on index line
        3. The line number indicator supports negative indexing.

        .. code-block:: python

            # Example
            code.highlight(
                3,          # highlight fourth line
                -1,         # last line
                "5-7"       # lines 5 through 7, inclusive
                "10:20,5"   # line 10, characters 20 through 25
            )

        All start positions are zero indexed.
        """
        for arg in args:
            if isinstance(arg, str) and ":" in arg:
                index, spec = self._parse_partial(arg)

                self.meta[index].highlight_partial.append(spec)
                continue

            # Argument is for a full line add it to the highlighting set
            self._set_highlight(arg, True)

    def highlight_off(self, *args):
        """Turns highlighting for one or more code lines. See
        :func:`Code.highlight` for a list of available highlight specifiers
        """
        for arg in args:
            if isinstance(arg, str) and ":" in arg:
                index, spec = self._parse_partial(arg)
                if index in self.meta:
                    # Only turn it off it was already on
                    try:
                        self.meta[index].highlight_partial.remove(spec)
                    except ValueError:
                        raise ValueError("Can only turn off existing partials")

                continue

            # Argument is for one or more full lines, turn them off
            self._set_highlight(arg, False)

    def highlight_all_off(self):
        """Removes all highlighting"""
        for value in self.meta.values():
            value.highlight = False
            value.highlight_partial = []

    def is_highlighted(self, line_index):
        if line_index not in self.meta:
            return False

        meta_info = self.meta[line_index]
        return meta_info.highlight or meta_info.highlight_partial

    # === Rendering
    def render_line(self, render_state, line, line_index):
        """Responsible for rendering the given line and appending the result
        into the :class:`RenderState` object.
        """
        if line_index in self.meta and self.meta[line_index].hidden:
            # No change to render_state, but may need to advance line count
            if render_state.doc.line_numbers_enabled:
                render_state.line_number += 1
            return

        if line_index in self.meta and self.meta[line_index].folded:
            # This is the parent line in a fold, display an indicator
            # instead
            output = CodeLine(lexer_spec=line.lexer_spec, has_newline=True)
            output.parts.append(CodePart(Fold, text=render_state.doc.fold_char))

            if render_state.doc.line_numbers_enabled:
                part = render_state.next_line_number_part()
                output.parts.insert(0, part)

            render_state.formatter.render_code_line(render_state, output)
            return

        # Handle the actual line, adding line numbers, dealing with
        # highlighting and wrapping it if needed
        if self.is_highlighted(line_index):
            line = self._apply_highlight(line_index)

        output = deepcopy(line)
        if render_state.doc.line_numbers_enabled:
            part = render_state.next_line_number_part()
            output.parts.insert(0, part)

        lwr = _LineWrapRenderer(render_state, output)
        lwr.run()

    # --- Highlighting Application
    @classmethod
    def _expand_parts(cls, line):
        """Creates a new list of parts expanding the text of each part into
        its own :class:`~purdy.parser.CodePart`, essentially creating parts
        consisting of a single letter.

        :param line: :class:`~purdy.parser.CodeLine` to expand
        :returns: list of :class:`~purdy.parser.CodePart` objects
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
        """Creates a new :class:`~purdy.parser.CodeLine` with highlight tokens
        at partial highlight spots

        :param line: :class:`~purdy.parser.CodeLine` to copy and transform
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
        output = CodeLine(line.lexer_spec, has_newline=line.has_newline)
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

    def _apply_highlight(self, line_index):
        """If there is highlighting to apply, creates a new
        :class:`~purdy.parser.CodeLine` as a copy of the given one but with
        highlight tokens applied. If there is no highlighting, just returns
        the given line.

        :param line_index: Index value of :class:`~purdy.parser.CodeLine`
            inside this `Code` object
        """
        if line_index not in self.meta:
            # No highlighting (this is checked here to remove "and" clauses
            # from below reducing line length)
            return self.lines[line_index]

        output = deepcopy(self.lines[line_index])

        if self.meta[line_index].highlight:
            # Highlight whole line, stick tokens at beginning and end
            output.parts.insert(0, CodePart(HighlightOn, ""))
            output.parts.append(CodePart(HighlightOff, ""))
        elif self.meta[line_index].highlight_partial:
            # Partial highlighting, insert tokens as needed inside the line
            output = self._chop_partial_highlight(output,
                self.meta[line_index].highlight_partial)

        # Else: no highlighting
        return output

# ---------------------------------------------------------------------------

class _LineWrapRenderer:
    """Splits a line up into multiple parts based on the wrap length and
    updates renders content with each new line."""
    def __init__(self, render_state, line):
        self.render_state = render_state
        self.formatter = render_state.formatter
        self.line = line

    def run(self):
        # If wrapping is off
        if self.render_state.doc.wrap is None:
            self.formatter.render_code_line(self.render_state, self.line)
            return

        # If the line is shorter than the wrap
        line_width = self.line.parts.text_length
        if line_width < self.render_state.doc.wrap:
            self.formatter.render_code_line(self.render_state, self.line)
            return

        chunkify = deepcopy(self.line)
        self._chunk_line(chunkify)

    def _reset_current_line(self):
        self.current = self.line.spawn()
        self.length = 0

    def _split_part(self, part):
        # Split line here, -ve value to get chars from RHS
        cut_at = self.render_state.doc.wrap - self.length
        left_of = part.text[0:cut_at]
        split_point = left_of.rfind(" ")

        if split_point == -1:
            # No split point in the text, render what we have so far
            self.formatter.render_code_line(self.render_state,
                self.current)

            # Set up for next line
            self._reset_current_line()
            self.current.parts.append(part)
            self.length += len(part.text)
            return None

        # Stuff everything to the left of the split point into the
        # current line and render it
        left = CodePart(part.token, part.text[:split_point + 1])
        self.current.parts.append(left)
        self.formatter.render_code_line(self.render_state, self.current)

        # Everything else goes into the next line
        self._reset_current_line()
        right = CodePart(part.token, part.text[split_point + 1:])
        return right

    def _chunk_line(self, chunkify):
        """Splits given line into chunks of rendered lines. Modifies line in
        place, so it what is passed in should be a copy."""
        self._reset_current_line()

        for part in chunkify.parts:
            self.length += len(part.text)
            if self.length > self.render_state.doc.wrap:
                right = self._split_part(part)
                while(right):
                    if len(right.text) > self.render_state.doc.wrap:
                        right = self._split_part(right)
                    else:
                        self.length = len(right.text)
                        self.current.parts.append(right)
                        break
            else:
                # Not a split point, Copy the CodePart into the wrapped line
                full = CodePart(part.token, part.text)
                self.current.parts.append(full)

        if len(self.current.parts) > 0:
            # Render whatever is left
            self.formatter.render_code_line(self.render_state, self.current)

# ===========================================================================

class StringSection(Section):
    def __init__(self, content=None):
        super().__init__()
        self.theme = EMPTY_THEME

        if content is None:
            self.lines = []
        elif isinstance(content, str):
            self.lines = [content, ]
        elif isinstance(content, list):
            self.lines = content
        else:
            raise ValueError("StringSection requires string or list of strings")

    def render_line(self, render_state, line, line_index):
        # Strings have no formatting, just append it
        render_state.content += line

# ===========================================================================

class Document(list):
    """Container for renderable :class:`Section` objects like :class:`Code`
    and :class:`StringSection`. Constructor optionally takes a `section` to
    include. Manages display attributes that get used across multiple sections
    like line numbering.
    """
    def __init__(self, sections=None):
        super().__init__()

        if isinstance(sections, Section):
            self.append(sections)
        elif sections is not None:
            for item in sections:
                self.append(item)

        self.background = None
        self.line_numbers_enabled = False
        self.starting_line_number = 1
        self.line_number_gap_char = " "
        self.wrap = None
        self.fold_char = "⠇"

# ---------------------------------------------------------------------------

class RenderState:
    """Encapsulates the data needed for rendering and will contain the
    rendered output of of a :class:`Document`.

    :param document: `Document` that will be rendered
    :param future_length: When calculating width for line numbers, add this
        value to the max length. Useful when the :class:`RenderState` needs to
        be created before content gets added to the :class:`Document`.
    """
    def __init__(self, document, future_length=0):
        self.doc = document
        self.content = ""
        self.line_number = None

        if document.line_numbers_enabled:
            self.line_number = document.starting_line_number

            max_line = document.starting_line_number + future_length
            for section in document:
                max_line += len(section.lines)

            self.line_number_width = int(math.log10(max_line) + 1)

    def next_line_number(self):
        """Gets the next line number and increments the count."""
        output = self.line_number
        self.line_number += 1
        return f"{output:{self.line_number_width}d} "

    def next_line_number_part(self):
        """Gets the next line number as a :class:`~purdy.parser.CodePart` and
        increments the count."""
        output = self.line_number
        self.line_number += 1
        return CodePart(LineNumber, f"{output:{self.line_number_width}d} ")

    def line_number_gap(self):
        """Returns a whitespace string the width of a line number, useful for
        when dealing with wrapping
        """
        # Width of line number plus a gutter
        return (self.line_number_width + 1) * " "
