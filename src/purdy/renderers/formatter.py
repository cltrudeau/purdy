# renderers/formatter.py
from copy import deepcopy

from purdy.content import Code, MultiCode
from purdy.parser import (CodeLine, CodePart, Fold, HighlightOff, HighlightOn,
    LineNumber, token_ancestor)

# =============================================================================

def conversion_handler(formatter_cls, container, exceptions):
    """Helper function for the most common case of rendering a :class:`Code`
    or :class:`MultiCode` object.

    :param formatter_cls: Reference to a class (not an object) to instantiate
        as the formatter for each `Code` block in the container
    :param container: `Code` or `MultiCode` object to translate
    """
    result = ""
    if isinstance(container, Code):
        container = MultiCode(container)

    for code_index in range(0, len(container)):
        formatter = formatter_cls()
        formatter.create_tag_map(container[code_index].theme, exceptions)
        result += formatter.format_doc(container, code_index)

    return result

# =============================================================================

class Formatter:
    def __init__(self):
        self.tag_map = {}
        self.newline = "\n"
        self.escape = lambda x:x

    def create_tag_map(self, theme, exceptions):
        for token, fg, bg, attrs in theme.values():
            self._map_tag(token, fg, bg, attrs, exceptions)

    def _map_tag(self, token, fg, bg, attrs, exceptions):
        raise NotImplementedError()

    def format_line(self, line, ancestor_list):
        """Abstract method that gets called for each code line to be rendered

        :param line: :class:`CodeLine` object to render
        :param ancestor_list: list of allowed base tokens. Tokens are
            hierarchical and this list specifies what parents are in the
            colour map.
        :returns: rendered text
        """
        raise NotImplementedError()

    # --- Base Formatting Code
    def get_decorated_lines(self, container, code_index):
        """Metadata in the :class:`Code` object changes what lines get
        rendered or not. This method returns a list of :class:`CodeLine`
        objects by applying the metadata decoration information to `Code`.

        :param container: :class:`MultiCode` container for `Code`
        :param code_index: index number of `Code` object in container
        :returns: list of :class:`CodeLine` objects
        """
        code = container[code_index]
        formatted_lines = []

        # Loop over lines in Code object
        for line_index, line in enumerate(code.lines):
            if line_index in code.meta and code.meta[line_index].hidden:
                continue

            if line_index in code.meta and code.meta[line_index].folded:
                # This is the parent line in a fold, display an indicator
                # instead
                output = CodeLine(lexer_spec=line.lexer_spec, has_newline=True)
                output.parts.append(CodePart(Fold, text=container.fold_char))

                if container.line_numbers_enabled:
                    line_no = container.line_number(code_index, line_index)
                    part = CodePart(LineNumber, line_no)
                    output.parts.insert(0, part)

                formatted_lines.append(output)
                continue

            # Handle highlighting and wrapping
            output = self._apply_highlight(code, line_index)
            wrapped = self._apply_wrapping(container, output)

            if container.line_numbers_enabled:
                # Apply line numbers to first wrapped line
                line_no = container.line_number(code_index, line_index)
                part = CodePart(LineNumber, line_no)
                wrapped[0].parts.insert(0, part)

            for piece in wrapped:
                formatted_lines.append(piece)

        return formatted_lines

    def format_doc(self, container, code_index):
        """Applies formatting to a :class:`Code` object based on its metadata,
        and for each :class:`CodeLine`, calls :method:`Format.format_line` to
        turn it into formatted text. Subclasses of class provide the
        implementation of `format_line` to produce rendered output.

        :param container: :class:`MultiCode` containing the `Code` object to
            format
        :param code_index: index number of `Code` inside the container
        :returns: Formatted string representation of the code
        """
        # Loop over the resulting CodeLines and render them
        result = ""
        code = container[code_index]
        ancestor_list = code.theme.colour_map.keys()
        for line in self.get_decorated_lines(container, code_index):
            result += self.format_line(line, ancestor_list)

        return result

    # --- Wrap Handling
    def _chunk_line(self, container, compare, output):
        """Splits next piece out of line based on wrapping settings

        :param container: :code:`MultiCode` that owns the line being wrapped
        :param compare: :code:`CodeLine` being worked on
        :param output: list of `CodeLine` objects that are the result of
            previous chunking

        :returns: remaining `CodeLine` to be chunked or None if done
        """
        wrapped = CodeLine(lexer_spec=compare.lexer_spec, has_newline=True)
        length = 0

        for part_count, part in enumerate(compare.parts):
            length += len(part.text)
            if length > container.wrap:
                # Split the line at this point
                cut_at = container.wrap - length   # -ve, chars from right
                left_of = part.text[0:cut_at]
                split_point = left_of.rfind(" ")

                if split_point == -1:
                    # No split point in the text, move it all into the next
                    # line
                    output.append(wrapped)

                    next_line = CodeLine(lexer_spec=compare.lexer_spec,
                        has_newline=True)
                    next_line.parts.extend(compare.parts[part_count:])
                    return next_line

                # Stuff everything to the left into the current line
                left = CodePart(part.token, part.text[:split_point + 1])
                wrapped.parts.append(left)
                output.append(wrapped)

                # Everything else goes into the next line
                next_line = CodeLine(lexer_spec=compare.lexer_spec,
                    has_newline=True)

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

    def _apply_wrapping(self, container, line):
        """Split a line up into multiple parts based on the wrap length.

        :param container: :class:`MultiCode` container specifying line wrap
            behaviour
        :param line: :class:`CodeLine` to be split into wrapped lines

        :returns: Returns a list of :class:`CodeLine` objects based on
            splitting the given one. If no wrap was needed the list contain
            the original :class:`CodeLine`
        """
        compare = deepcopy(line)

        # If wrapping is off, or the line is shorter than the wrap
        if container.wrap is None or line.parts.text_length < container.wrap:
            return [compare]

        # Perform wrapping
        #
        # When a line is split into more than two, the wrap of the second line
        # starts where the second line got split. Wrapping at 20 does not mean
        # wrapping every 20 characters, it means no more than 20 past the last
        # splitting point
        result = []

        while(compare):
            compare = self._chunk_line(container, compare, result)

        # Match the newline state of the last line
        result[-1].has_newline = line.has_newline
        return result

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

    def _apply_highlight(self, code, line_index):
        """Creates a new :class:`CodeLine` as a copy of the given one but
        with highlight tokens applied.

        :param code: :class:`Code` container
        :param line_index: Index value of `CodeLine` inside the :class:`Code`
            container to  highlight
        """
        output = deepcopy(code.lines[line_index])
        if line_index not in code.meta:
            # No highlighting (this is checked here to remove "and" clauses
            # from below reducing line length)
            return output

        if code.meta[line_index].highlight:
            output.parts.insert(0, CodePart(HighlightOn, ""))
            output.parts.append(CodePart(HighlightOff, ""))
        elif code.meta[line_index].highlight_partial:
            # Split the line up as needed for partial highlighting
            output = self._chop_partial_highlight(output,
                code.meta[line_index].highlight_partial)

        # Else: no highlighting
        return output

# ---------------------------------------------------------------------------

class StrFormatter(Formatter):
    ### Uses str.format() to create stylized output from code; assumes the
    # ._map_tag() method populated using {text} for any token text to be
    # inserted

    def format_line(self, line, ancestor_list):
        result = ""
        for part in line.parts:
            token = token_ancestor(part.token, ancestor_list)
            token_text = self.escape(part.text)

            try:
                marker = self.tag_map[token]
                result += marker.format(text=token_text)
            except KeyError:
                result += token_text

        if line.has_newline:
            result += self.newline

        return result
