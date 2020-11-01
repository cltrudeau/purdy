from purdy.parser import FoldedCodeLine

# =============================================================================
# Plain Colourizer: the colourizer that doesn't do colour, handles plain text
# augmentation like line numbers for uncolourized display

class PlainColourizer:
    @classmethod
    def colourize(cls, code_line):
        """Returns the plain text version of the code line.

        :param code_line: a :class:`CodeLine` object to process
        """
        if isinstance(code_line, FoldedCodeLine):
            return '⋮'

        output = []
        if code_line.line_number != -1:
            output.append( cls.line_number(code_line.line_number) )

        output.extend([part.text for part in code_line.parts])
        return ''.join(output)

    @classmethod
    def line_number(cls, num):
        """Returns a colourized version of a line number"""
        return f'{num:3} '
