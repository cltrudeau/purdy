# typewriter.py
#
# Utility class for emulating the typing of a Code object
from copy import copy, deepcopy
from collections import namedtuple

from pygments.token import Comment, Generic, Text, Whitespace
from textual.content import Content as TContent
from textual.markup import MarkupTokenizer

from purdy.parser import CodePart, CURSOR, CURSOR_CHAR, LineNumber, token_is_a
from purdy.renderers.textual import TextualFormatter, _CODE_TAG_EXCEPTIONS
from purdy.tui.tui_content import EscapeText

# ===========================================================================

TypewriterOutput = namedtuple("TypewriterOutput", ["text", "state"])


class _CodeTypewriter:
    def __init__(self, base_render_state, src_code, skip_comments,
            skip_whitespace):
        self.base_render_state = copy(base_render_state)
        self.base_render_state.formatter = TextualFormatter(src_code,
            _CODE_TAG_EXCEPTIONS)

        self.src_code = src_code
        self.skip_comments = skip_comments
        self.skip_whitespace = skip_whitespace

        self.is_console = src_code.parser.lexer_spec.console

    def _skip_part(self, part, state="P"):
        self.typing_line.parts.append(part)
        self.typing_line.parts.append(CURSOR)

        self.typing_rs.formatter.render_code_line(self.typing_rs,
            self.typing_line)

        result = TypewriterOutput(
            text=self.cached_rs.content + self.typing_rs.content,
            state=state
        )
        self.results.append(result)

        # Remove the cursor, then reset for # the next line
        del self.typing_line.parts[-1]  # cursor
        self.typing_rs.content = TContent()

    def _run(self):
        """Returns a list of :class:`textual.content.Content` objects
        representing a series of steps used to emulate typing of this source
        object.  """
        self.results = []
        self.cached_rs = copy(self.base_render_state)
        self.cached_rs.content = TContent()

        for src_line in self.src_code.lines:
            self.typing_rs = copy(self.cached_rs)
            self.typing_rs.content = TContent()
            self.typing_line = src_line.spawn()

            if self.typing_rs.doc.line_numbers_enabled:
                num = self.cached_rs.next_line_number()
                self.cached_rs.content += \
                    self.typing_rs.formatter.part_to_content(LineNumber, num)

            # Handle multi-line console output
            if self.is_console:
                first_token = src_line.parts[0].token

                is_output = token_is_a(first_token, Generic.Output)
                is_output |= not token_is_a(first_token, Generic.Prompt)

                if is_output:
                    self.typing_rs.formatter.render_code_line(self.typing_rs,
                        src_line)

                    result = TypewriterOutput(
                        text=self.cached_rs.content + self.typing_rs.content,
                        state=None
                    )
                    self.results.append(result)

                    self.cached_rs.formatter.render_code_line(self.cached_rs,
                        src_line)
                    self.typing_rs.content = TContent()
                    continue

            # Typewriter-ize the line's parts
            for src_part in src_line.parts:
                src_token = src_part.token
                part = CodePart(token=src_token, text="")

                if self.is_console and token_is_a(src_token, Generic.Prompt):
                    # Don't animate prompts
                    self._skip_part(src_part, state="W")
                    continue

                if self.skip_comments and token_is_a(src_token, Comment):
                    # Don't animate comments
                    self._skip_part(src_part)
                    continue

                if self.skip_whitespace:
                    # Don't animate whitespace; this can be a specific token,
                    # or just blank text
                    skip_it = token_is_a(src_token, Whitespace)

                    if token_is_a(src_token, Text):
                        skip_it |= src_part.text.isspace()

                    if skip_it:
                        self._skip_part(src_part)
                        continue

                for char in src_part.text:
                    # Add the character to the part, put it in the line and
                    # put that in the results listing
                    part.text += char
                    self.typing_line.parts.append(part)
                    self.typing_line.parts.append(CURSOR)

                    self.typing_rs.formatter.render_code_line(self.typing_rs,
                        self.typing_line)

                    result = TypewriterOutput(
                        text=self.cached_rs.content + self.typing_rs.content,
                        state="P"
                    )
                    self.results.append(result)

                    # Remove the partial part and the cursor, then reset for
                    # the next line
                    del self.typing_line.parts[-1]  # cursor
                    del self.typing_line.parts[-1]  # partial part
                    self.typing_rs.content = TContent()

                self.typing_line.parts.append(src_part)

            # Update the cached result with the final value of line
            self.cached_rs.formatter.render_code_line(self.cached_rs,
                self.typing_line)

        return self.results

    def _old_run(self):
        """Returns a list of :class:`textual.content.Content` objects
        representing a series of steps used to emulate typing of this source
        object.  """
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


def code_typewriterize(render_state, src_code, skip_comments=True,
        skip_whitespace=True):
    """Outputs a list of :class:`textual.content.Content` objects to be used
    as typing animations"""
    tw = _CodeTypewriter(render_state, src_code, skip_comments, skip_whitespace)
    return tw._run()

# ---------------------------------------------------------------------------

MARKUP_CURSOR = "[white]" + CURSOR_CHAR + "[/]"

def _plain_typewriterize(results, base_render_state, rendered, line):
    current = TContent()

    if base_render_state.doc.line_numbers_enabled:
        num = base_render_state.next_line_number()
        current += base_render_state.formatter.part_to_content(LineNumber, num)

    for char in line:
        current += char
        results.append(rendered + current + CURSOR_CHAR)

    return current


def textual_typewriterize(base_render_state, section):
    results = []
    rendered = TContent()
    tokenizer = MarkupTokenizer()
    tag = ""

    for line in section.lines:
        if isinstance(line, EscapeText):
            # Handle plain text as a special case
            result = _plain_typewriterize(results, base_render_state, rendered,
                line)
            rendered += result
            continue

        # Non-escaped text, possibility that it contains markup
        current = ""

        if base_render_state.doc.line_numbers_enabled:
            num = base_render_state.next_line_number()
            rendered += base_render_state.formatter.part_to_content(LineNumber,
                num)

        for token in tokenizer(line, ("inline", "")):
            if token.name == "text":
                for char in token.value:
                    current += char
                    output = TContent.from_markup(current + MARKUP_CURSOR)
                    results.append(rendered + output)
            elif token.name == "eof":
                pass
            elif token.name == "end_tag":
                tag += token.value
                current += tag
                output = TContent.from_markup(current + MARKUP_CURSOR)
                results.append(rendered + output)
                tag = ""
            else:
                # Token is some part of a tag, accumulate it in current
                tag += token.value

        rendered += TContent.from_markup(line + "\n")

    return results
