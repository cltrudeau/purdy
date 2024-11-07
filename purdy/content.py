"""
Content
=======

Reperesntations of source code are found in this module.
"""
import ast, asttokens, os
from copy import deepcopy

from purdy.colour import COLOURIZERS
from purdy.parser import FoldedCodeLine, parse_source

#import logging
#logging.basicConfig(filename='debug.log', level=logging.DEBUG)
#logger = logging.getLogger()

# =============================================================================

class Code:
    """Represents source code from the user.

    :param filename: name of a file to read for content. If both this and
                     `text` is given, `filename` is used first

    :param text: a string containing code

    :param lexer_name: name of lexer to use to tokenize the code, defaults to
                       'detect', attempting to auto detect the type of
                       content. See :class:`purdy.parser.PurdyLexer` for a
                       list of available lexers.

    :param purdy_lexer: if lexer_name is "custom" this parameter is expected
                         to contain a purdy.parser.PurdyLexer object.
    """

    def __init__(self, filename='', text='', lexer_name='detect',
            purdy_lexer=None):
        self.source = ''

        if filename:
            filename = os.path.abspath(filename)
            with open(filename) as f:
                self.source += f.read()

        if text:
            self.source += text

        self.source = self.source.rstrip('\n')

        from purdy.parser import PurdyLexer
        if lexer_name == 'detect':
            self.lexer = PurdyLexer.factory_from_source(self.source)
        elif lexer_name == 'custom':
            self.lexer = purdy_lexer
        else:
            self.lexer = PurdyLexer.factory_from_name(lexer_name)

    def remove_double_blanks(self, trim_whitespace=True):
        """Removes the second of two blanks in a row. If trim_whitespace is
        True (default) a line with only whitespace is considered blank,
        otherwise it only looks for \\n"""
        lines = self.source.split('\n')
        output = []

        previous = 'asdf'
        for line in lines:
            if trim_whitespace \
                    and previous.strip() == '' and line.strip() == '':
                continue
            else:
                if previous == '' and line == '':
                    continue

            output.append(line)
            previous = line

        self.source = '\n'.join(output)
        return self

    def remove_lines(self, line_no, count=1):
        """Removes one or more lines from the source listing.

        :param line_no: number of the line to remove, 1-indexed
        :param count: number of lines to remove, defaults to 1
        """
        lines = self.source.split('\n')
        start = line_no - 1
        end = start + count
        del lines[start:end]
        self.source = '\n'.join(lines)
        return self

    def replace_line(self, line_no, content):
        """Replaces the given line with new content

        :param line_no: number of the line to replace, 1-indexed
        :param content: content to replace it with
        """
        lines = self.source.split('\n')
        lines[line_no - 1] = content
        self.source = '\n'.join(lines)
        return self

    def inline_replace(self, line_no, pos, content):
        """Replaces the contents of a line starting at pos with the new
        content

        :param line_no: number of the line to replace, 1-indexed
        :param pos: position number to start the replacement at, 1-indexed
        :param content: content to replace with
        """
        lines = self.source.split('\n')
        lines[line_no - 1] = lines[line_no - 1][:pos - 1]
        lines[line_no - 1] += content
        self.source = '\n'.join(lines)
        return self

    def insert_line(self, line_no, content):
        """Inserts the given line into the source, pushing the content down
        from the given line number

        :param line_no: number of the line to insert at, 1-indexed
        :param content: content to insert
        """
        lines = self.source.split('\n')
        lines.insert(line_no - 1, content)
        self.source = '\n'.join(lines)
        return self

    def _descend_ast(self, atok, parent, local_name, name_parts):
        for node in ast.iter_child_nodes(parent):
            if node.__class__ in [ast.FunctionDef, ast.ClassDef] \
                    and node.name == local_name:
                if len(name_parts) == 0:
                    # Found the node, return the code
                    return atok.get_text(node) + "\n"

                # Found a function or class, but looking for a child of it
                return self._descend_ast(atok, node, name_parts[0],
                    name_parts[1:])

            if node.__class__ == ast.Assign and \
                    node.first_token.string == local_name and \
                    len(name_parts) == 0:
                return atok.get_text(node) + "\n"

        return ''

    def python_portion(self, name, header=None):
        """Treates the source in this object as Python and then finds either
        the named function, class, or assigned variable and replaces the
        source with only the found item.

        .. warning:: If the named item is not found your source will be empty!

        :param name: dot notated name of a function or class. Examples:
                     `Foo.bar` would find the `bar` method of class `Foo` or
                     an inner function named `bar` in a function named `Foo`
        :param header: optionally include another part of the source file
                       before the parsed content. Typically used to include
                       the header portion of a file. If given an integer, it
                       will include the first X number of lines. If given a
                       tuple "(x, y)" includes lines from x to y (inclusive)
        """
        output = ""
        if header is not None:
            content = []
            lines = self.source.split('\n')
            if isinstance(header, int):
                content += lines[0:header]
            elif isinstance(header, tuple):
                start = header[0] - 1
                end = header[1]
                content += lines[start:end]

            output = "\n".join(content) + "\n"

        atok = asttokens.ASTTokens(self.source, parse=True)
        name_parts = name.split('.')
        output += self._descend_ast(atok, atok.tree, name_parts[0],
            name_parts[1:])

        self.source = output
        return self

    def left_justify(self):
        """Removes a consistent amount of leading whitespace from the front of
        each line so that at least one line is left-justified.

        .. warning:: will not work with mixed tabs and spaces
        """
        lines = self.source.split('\n')
        leads = [len(line) - len(line.lstrip()) for line in lines if \
            len(line.strip())]
        if not leads:
            # only blank lines, do nothing
            return

        min_lead = min(leads)
        output = []
        for line in lines:
            if len(line.lstrip()):
                output.append(line[min_lead:])
            else:
                output.append(line)

        self.source = '\n'.join(output)
        return self

    def fold_lines(self, start, end):
        """Call this method to replace one or more lines with a vertical
        elipses, i.e. a fold of the code.

        :param start: line number of the listing to start code folding on.
                      1-indexed.
        :param end: line number to fold until, inclusive (1-indexed).
        """
        lines = self.source.split('\n')

        self.source = '\n'.join(lines)

        size = end - start + 1
        lines[start - 1] = '⋮'

        if size > 1:
            del lines[start:end]

        self.source = '\n'.join(lines)

        return self

    def subset(self, start, end):
        """Returns a new Code object containing just the subset of lines
        identified in this call

        :param start: line number of the listing to start the subset at.
                      1-indexed
        :param end: line number to finish the subset on, inclusive.  1-indexed.

        :returns: Code object
        """
        code = deepcopy(self)
        if end < start:
            raise AttributeError('Value of end must be bigger than start')

        lines = self.source.split('\n')
        lines = lines[start - 1:end]
        code.source = '\n'.join(lines)
        return code

# -----------------------------------------------------------------------------

class RenderHook:
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
                    self.append_code(item)


    def set_display(self, mode='plain', render_hook=None):
        """Code can be displayed using a variety of methods, from colourized
        text to the urwid TUI client. This method sets the options to control
        how rendering is done.

        :param mode: a key from :attr:`purdy.colour.COLOURIZERS` indicating
                     which colourizer routine is used to colour the source in
                     this box. Defaults to 'plain'.
        :param render_hook: an optional hook the box calls when actions are
                            done on the box. Used by the TUI client so that
                            when something changes in the it is reflected in
                            the TUI.
        """
        self.colourizer = COLOURIZERS[mode]

        if render_hook:
            self.render_hook = render_hook

    #--- Add/Remove Line Methods
    def positive_position(self, position):
        original = position
        size = len(self.lines)

        if position < 0:
            position = size + position + 1

        # check within bounds
        if position <= 0 or position > size:
            if original == 0:
                raise IndexError('position is 1-indexed, 0 is invalid')

            if original < 0:
                raise IndexError( (f'position {original} translated to '
                    f'{position}, is outside range 1-{size}') )

            raise IndexError(f'position {position} outside range 1-{size}')

        return position

    def append_code(self, code):
        """Parses contents of a :class:`Code` object and appends it to this
        box. Has a side effect of changing the listing's colour palette to
        that of the code object sent in."""
        lines = parse_source(code.source, code.lexer)
        self.insert_lines(0, lines)

    def get_line(self, position):
        """Returns the line at the given position. Lines are 1-indexed, 0
        means the last line, negative indexing supported

        :param position: position of line to return
        """
        if position == 0:
            position = len(self.lines)
        else:
            position = self.positive_position(position)

        return self.lines[position - 1]

    def insert_lines(self, position, lines):
        """Inserts a line at the given position. Pushes content down, so
        a line inserted at position 1 becomes the new first item.

        :param position: 1-indexed position in the listing. Supports negative
                         indexing and a special value of 0 to indicate
                         appending to the list
        :param lines: lines to insert
        """
        # loop through lines and insert them, assigning a new line number if
        # needed
        if position == 0:
            # special case, insert becomes append
            position = len(self.lines) + 1
        else:
            position = self.positive_position(position)

        new_lines = deepcopy(lines)

        for count, line in enumerate(new_lines):
            if self.starting_line_number > -1:
                line.line_number = position + count + \
                    self.starting_line_number - 1

            self.lines.insert(count + position - 1, line)
            self.render_hook.line_inserted(self, position + count, line)

        if self.starting_line_number > -1:
            self.reset_line_numbers()

    def replace_line(self, position, line):
        """Replaces the line at the given position with the given
        :class:`CodeLine` object"""
        position = self.positive_position(position)

        new_line = deepcopy(line)
        if self.starting_line_number != -1:
            new_line.line_number = position + self.starting_line_number - 1

        self.lines[position - 1] = new_line
        self.render_hook.line_changed(self, position, new_line)

    def remove_lines(self, position, size=1):
        position = self.positive_position(position)

        for x in range(1, size + 1):
            del self.lines[position - 1]

            self.render_hook.line_removed(self, position)

        if self.starting_line_number > -1:
            self.reset_line_numbers()

    def clear(self):
        self.lines = []
        self.render_hook.clear()

    def copy_lines(self, position, size=1):
        """Returns a copy of the lines for the given position and size

        :param position: 1-index position in the listing, supports negative
                         indexing
        :param size: number of lines to return, defaults to 1
        """
        position = self.positive_position(position)
        result = []

        for count in range(0, size):
            result.append( deepcopy(self.lines[position - 1 + count]) )

        return result

    def fold_lines(self, start, end):
        """Call this method to replace one or more lines with a vertical
        elipses, i.e. a fold of the code.

        :param start: line number of the listing to start code folding on.
                      1-indexed.
        :param end: line number to fold until, inclusive (1-indexed).
        """
        size = end - start + 1

        replace_line = FoldedCodeLine(size)
        self.lines[start - 1] = replace_line
        self.render_hook.line_changed(self, start, replace_line)

        if size > 1:
            #remove rest of lines in fold, line numbers will be fixed when
            # remove_lines() calls reset_line_numbers()
            self.remove_lines(start + 1, size - 1)

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

    def reset_line_numbers(self):
        """Reset the line numbers."""
        # Because of code folding possibly advancing the numbering, have to
        # check the whole listing
        current_position = 1
        line_number = self.starting_line_number

        if len(self.lines) > 0 and isinstance(self.lines[0], FoldedCodeLine):
            line_number = self.starting_line_number + self.lines[0].size

        for line in self.lines:
            if not isinstance(line, FoldedCodeLine) and \
                    line.line_number != line_number:
                # changing the line number, trigger the hook
                line.line_number = line_number
                self.render_hook.line_changed(self, current_position, line)

            current_position += 1
            if isinstance(line, FoldedCodeLine):
                line_number += line.size
            else:
                line_number += 1

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
