from .base import BaseColourizer
from purdy.parser import FoldedCodeLine, token_ancestor

# =============================================================================
# Plain Colourizer: the colourizer that doesn't do colour, handles plain text
# augmentation like line numbers for uncolourized display

class PlainColourizer(BaseColourizer):
    def colourize(self, code_line):
        """Returns the plain text version of the code line.

        :param code_line: a :class:`CodeLine` object to process
        """
        if isinstance(code_line, FoldedCodeLine):
            return '⋮'

        output = []
        if code_line.line_number != -1:
            output.append( self.line_number(code_line.line_number) )

        output.extend([part.text for part in code_line.parts])
        return ''.join(output)

    def line_number(self, num):
        """Returns a colourized version of a line number"""
        return f'{num:3} '
