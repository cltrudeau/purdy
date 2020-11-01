# =============================================================================
# Base Colourizer: base class for colourizers

class BaseColourizer:
    def __init__(self, palette):
        self.palette = palette

    def colourize(self, code_line):
        """Returns a string containing a colourized line of code.

        :param code_line: a :class:`CodeLine` object to process
        """
        raise NotImplementedError()

    def line_number(self, num):
        """Returns a colourized code string with a line number prefix"""
        raise NotImplementedError()
