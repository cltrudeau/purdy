# content.py
#
# Code encapsulation
from pathlib import Path

from purdy.parser import Parser

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
