"""
Filters
=======

Source code processing tools used by :class:`purdy.content.Code`.
"""
import ast, asttokens

# =============================================================================
# Code Filters
#
# Filters are classes that implement a `filter(self, source)` method which
# takes a string containing source code and returns a modified version
# =============================================================================

class python_extractor:
    """Expects the source being filtered to be valid Python, searches it for
    the given name which can be a function, class, or assigned variable.
    Filter returns the found items.

    .. warning:: If the named item is not found your source will be empty!

    :param name: dot notated name of a function or class. Examples:
                 `Foo.bar` would find the `bar` method of class `Foo` or
                 an inner function named `bar` in a function named `Foo`
    """
    def __init__(self, name):
        self.name = name

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

    def filter(self, source):
        atok = asttokens.ASTTokens(source, parse=True)
        name_parts = self.name.split('.')
        output = self._descend_ast(atok, atok.tree, name_parts[0],
            name_parts[1:])
        return output

# -----------------------------------------------------------------------------

class remove_lines:
    """Removes one or more lines from a source code block. Takes a series of
    line numbers to remove given as arguments to the class. Line numbers can
    either be an integer a tuple, where the tuple indicates the line number
    and number of lines after it.  The list of lines must be in ascending
    order.

    Line numbers are 1-indexed.
    """

    def __init__(self, *args):
        self.numbers = args

    def filter(self, source):
        lines = source.split("\n")
        delta = 0

        for number in self.numbers:
            if isinstance(number, int):
                remove = number - delta
                del lines[remove - 1]     # 1-indexed
                delta += 1
            elif isinstance(number, tuple):
                remove, count = number
                remove = remove - delta
                for _ in range(0, count):
                    del lines[remove - 1] # 1-indexed

                delta += count

        return "\n".join(lines)

# -----------------------------------------------------------------------------

class remove_double_blanks:
    """Removes the second of two blanks in a row. If trim_whitespace is
    True (default) a line with only whitespace is considered blank,
    otherwise it only looks for \\n"""

    def __init__(self, trim_whitespace=True):
        self.trim_whitespace = trim_whitespace

    def filter(self, source):
        ends_in_blank = source[-1] == "\n"
        lines = source.split("\n")
        output = []

        for line in lines:
            if line == "" or (self.trim_whitespace and line.strip() == ""):
                continue

            output.append(line)

        result = "\n".join(output)
        if ends_in_blank:
            result += "\n"

        return result

# -----------------------------------------------------------------------------

class left_justify:
    """Removes a consistent amount of leading whitespace from the front of
    each line so that at least one line is left-justified.

    .. warning:: will not work with mixed tabs and spaces
    """

    def filter(self, source):
        lines = source.split('\n')
        leads = [len(line) - len(line.lstrip()) for line in lines if \
            len(line.strip())]
        if not leads:
            # only blank lines, do nothing
            return source

        min_lead = min(leads)
        output = []
        for line in lines:
            if len(line.lstrip()):
                output.append(line[min_lead:])
            else:
                output.append(line)

        return "\n".join(output)
