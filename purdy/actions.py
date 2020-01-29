# =============================================================================
# Actions
# =============================================================================

import random
from enum import Enum

from pygments.token import Generic

from purdy.content import CodeToken

# =============================================================================

class AppendAll:
    def __init__(self, code_box, code_blob):
        self.code_box = code_box
        self.code_blob = code_blob

    def setup(self, settings):
        self.code_box.append_tokens(self.code_blob.tokens)

    def next(self, key):
        raise StopIteration


class ReplaceAll(AppendAll):
    def setup(self, settings):
        # Replace is just like Append, but clear the box first
        self.code_box.clear()
        super().setup(settings)

# -----------------------------------------------------------------------------

class State(Enum):
    WAITING = 0
    TYPING  = 1


class AppendTypewriter:
    def __init__(self, code_box, code_blob):
        self.code_box = code_box
        self.code_blob = code_blob
        self.num_tokens = len(self.code_blob.tokens)

    def setup(self, settings):
        # delay settings
        self.typing_delay = settings['delay'] / 1000
        self.variance = settings['delay_variance']

        # current token 
        self.current_token = 0
        self.typing_queue = []
        self.typing_token = None

        # type tokens until first prompt
        self.show_tokens()
        self.state = State.WAITING

    def show_tokens(self):
        # adds tokens to the CodeListBox stopping after a prompt
        for token in self.code_blob.tokens[self.current_token:]:
            self.current_token += 1
            self.code_box.append_token(token)

            if token.token_type == Generic.Prompt:
                # stop at first prompt encountered
                break

    @property
    def delay_until_next_letter(self):
        vary_by = random.randint(0, 2 * self.variance) - self.variance
        return self.typing_delay + (vary_by / 1000)

    def next(self, key):
        # if we've output all the code, we are done
        if self.current_token >= self.num_tokens:
            raise StopIteration

        if self.state == State.TYPING and key is not None:
            # called due to a keypress, we're busy typing so ignore it
            return -1

        if self.state == State.WAITING:
            # got a keypress: start typing
            self.state = State.TYPING

        # state is State.TYPING
        if self.typing_queue == []:
            # nothing in typing queue, get next token to type
            token = self.code_blob.tokens[self.current_token]
            self.current_token += 1

            if token.text == '\n':
                # hit a CR, add a new line to our output, leave typewriter
                # mode, print tokens until next prompt
                self.code_box.append_newline()
                self.show_tokens()
                self.state = State.WAITING
                return -1
            elif token.text == '':
                # lexer spits out empty text sometimes, need to ignore it,
                # ask for an immediate call-back to invoke next letter in the
                # queue
                return 0
            else:
                # insert first letter into our text widget, put the rest in
                # the typing queue, set callback timer for next letter
                self.code_box.append_text(token.colour, token.text[0])
                self.typing_queue = list(token.text[1:])
                self.typing_token = token

                return self.delay_until_next_letter
        else:
            # typing queue has letters in it, get the next letter and add it
            # to our widget
            letter = self.typing_queue.pop(0)
            self.code_box.append_text(self.typing_token.colour, letter)

            return self.delay_until_next_letter


class ReplaceTypewriter(AppendTypewriter):
    def setup(self, settings):
        # Replace is just like Append, but clear the box first
        self.code_box.clear()
        super(ReplaceTypewriter, self).setup(settings)

# =============================================================================

class Highlight:
    def __init__(self, code_box, line_number, highlight):
        self.code_box = code_box
        self.line_number = line_number
        self.highlight = highlight

    def setup(self, settings):
        pass

    def next(self, key):
        numbers = self.line_number
        if isinstance(self.line_number, int):
            numbers = [self.line_number]

        for number in numbers:
            self.code_box.body.contents[number].set_highlight(
                self.highlight)

        raise StopIteration

# =============================================================================

class StopMovie:
    def __init__(self, screen):
        self.screen = screen

    def setup(self, settings):
        pass

    def next(self, key):
        self.screen.movie_mode = -1

        raise StopIteration
