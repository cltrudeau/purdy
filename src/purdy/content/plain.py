# handlers/plain.py
#
# Content handlers that transform tokenized text into plain text
from purdy.content import base

# ===========================================================================

class _PlainMixin:
    def output_line(self, index):
        """Transforms a tokenized line into a plain text string, modifying it
        based on the current settings for the object."""
        fold_count = self.fold_count(index)
        if fold_count:
            if fold_count == 1:
                return "⠇\n"

            # If you get here, then it wasn't the starting point in the fold
            return None

        # Transform line into plain text
        if self.wrap:
            wrapped = self.wrap_line(index)
        else:
            wrapped = [self.lines[index]]

        output = ""
        for line in wrapped:
            for part in line.parts:
                output += part.text

            if line.has_newline:
                output += "\n"

        return output


class Code(base._Code, _PlainMixin):
    pass


class TextCode(base._TextCode, _PlainMixin):
    pass
