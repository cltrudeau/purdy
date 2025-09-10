# typewriter.py
#
# Utility class for emulating the typing of a Code object
from copy import deepcopy

from pygments.token import Comment, Generic, Text, Whitespace
from textual.markup import MarkupTokenizer

from purdy.parser import CodePart, token_is_a

# ===========================================================================

class _CodeTypewriter:
    def __init__(self, src_code, skip_comments, skip_whitespace):
        self.src_code = src_code
        self.skip_comments = skip_comments
        self.skip_whitespace = skip_whitespace

        self.is_console = src_code.parser.lexer_spec.console

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

    def _skip_part(self, text):
        self.part.text = text
        self._commit_part()
        del self.current.lines[-1]

    def _run(self):
        """Returns a list of `Code` objects representing a series of steps
        used to emulate typing of this source object.
        """
        prev_was_output = False
        for src_line in self.src_code.lines:
            # Handle multi-line console output
            if self.is_console:
                first_token = src_line.parts[0].token

                is_output = token_is_a(first_token, Generic.Output)
                is_output |= not token_is_a(first_token, Generic.Prompt)

                if is_output:
                    if prev_was_output:
                        # nth output line, don't commit a new Code object,
                        # just update the previous one
                        prev_code = self.results[-1]
                        line = deepcopy(src_line)
                        prev_code.lines.append(line)
                        continue
                    else:
                        # First output line
                        prev_was_output = True
                        self.current.lines.append(src_line)
                        self.results.append(self.current)

                        # Reset for the next pass
                        self.current = deepcopy(self.current)
                        continue
                else:
                    prev_was_output = False

            self.line = src_line.spawn()

            for src_part in src_line.parts:
                src_token = src_part.token
                self.part = CodePart(token=src_token, text="")

                if self.is_console and token_is_a(src_token, Generic.Prompt):
                    # Don't animate prompts
                    self._skip_part(src_part.text)
                    continue

                if self.skip_comments and token_is_a(src_token, Comment):
                    # Don't animate comments
                    self._skip_part(src_part.text)
                    continue

                if self.skip_whitespace:
                    # Don't animate whitespace; this can be a specific token,
                    # or just blank text
                    skip_it = token_is_a(src_token, Whitespace)

                    if token_is_a(src_token, Text):
                        skip_it |= src_part.text.isspace()

                    if skip_it:
                        self._skip_part(src_part.text)
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


def code_typewriterize(src_code, skip_comments=True, skip_whitespace=True):
    tw = _CodeTypewriter(src_code, skip_comments, skip_whitespace)
    return tw._run()

# ---------------------------------------------------------------------------

def textual_typewriterize(content):
    results = []
    tokenizer = MarkupTokenizer()
    current = ""

    for token in tokenizer(content, ("inline", "")):
        if token.name == "text":
            for char in token.value:
                current += char
                results.append(current)
        elif token.name == "eof":
            pass
        elif token.name == "end_tag":
            current += token.value
            results.append(current)
        else:
            # Token is some part of a tag except the end of it, accumulate
            # it in current
            current += token.value

    return results

# ---------------------------------------------------------------------------

def string_typewriterize(content):
    results = []
    current = ""

    for char in content:
        current += char
        results.append(current)

    return results
