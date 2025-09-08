# typewriter.py
#
# Utility class for emulating the typing of a Code object
from copy import deepcopy

from pygments.token import Comment, Text, Whitespace

from purdy.parser import CodePart, token_is_a

# ===========================================================================

class Typewriter:
    @classmethod
    def typewriterize(cls, src_code, skip_comments=True, skip_whitespace=True):
        tw = Typewriter(src_code, skip_comments, skip_whitespace)
        return tw._run()

    def __init__(self, src_code, skip_comments, skip_whitespace):
        self.src_code = src_code
        self.skip_comments = skip_comments
        self.skip_whitespace = skip_whitespace

        self.current = src_code.spawn()
        self.results = []

    def _commit_part(self):
        self.line.parts.append(self.part)
        self.current.lines.append(self.line)

        self.results.append(self.current)

        # Reset for the next pass
        self.current = deepcopy(self.current)
        self.line = deepcopy(self.line)
        self.part = deepcopy(self.part)

    def _run(self):
        """Returns a list of `Code` objects representing a series of steps
        used to emulate typing of this source object.
        """
        for src_line in self.src_code.lines:
            self.line = src_line.spawn()

            for src_part in src_line.parts:
                self.part = CodePart(token=src_part.token, text="")

                if self.skip_comments and token_is_a(src_part.token, Comment):
                    # Don't animate comments
                    self.part.text = src_part.text
                    self._commit_part()
                    del self.current.lines[-1]
                    continue

                if self.skip_whitespace:
                    # Don't animate whitespace; this can be a specific token,
                    # or just blank text
                    skip_it = token_is_a(src_part.token, Whitespace)

                    if token_is_a(src_part.token, Text):
                        skip_it |= src_part.text.isspace()

                    if skip_it:
                        self.part.text = src_part.text
                        self._commit_part()
                        del self.current.lines[-1]
                        continue

                for char in src_part.text:
                    # Add the character to the part, put it in the line and
                    # put that in the results listing
                    self.part.text += char
                    self._commit_part()

                    del self.current.lines[-1]
                    del self.line.parts[-1]

                self.line.parts.append(self.part)
            self.current.lines.append(self.line)

        return self.results
