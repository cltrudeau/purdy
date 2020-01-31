# =============================================================================
# Actions
# =============================================================================

import random
from enum import Enum

from purdy.content import Animate

# =============================================================================

class AppendAll:
    """Appends the code to the code box. All work is done in the setup()
    phase, does not wait for a key press.
    """
    def __init__(self, code_box, code_blob):
        """Constructor

        :param code_box: a :class:`CodeBox` widget where the code will be 
            presented
        :param code: a :class:`Code` object containing code to post
        """
        self.code_box = code_box
        self.code_blob = code_blob

    def setup(self, settings):
        for line in self.code_blob.lines:
            self.code_box.add_line(line.markup)

    def next(self, key):
        raise StopIteration


class ReplaceAll(AppendAll):
    """Same as :class:`AppendAll` except it clears the code box before
    inserting the code.
    """
    def setup(self, settings):
        # Replace is just like Append, but clear the box first
        self.code_box.clear()
        return super().setup(settings)

# -----------------------------------------------------------------------------

class State(Enum):
    WAITING = 0
    TYPING  = 1


class AppendTypewriter:
    """Appends the code to the code box using a typewriter animation. Meant to
    be used with console-style (REPL) scripts. Prompts are printed immediately,
    anything after a prompt waits for a key press. Each key press will cause
    the typewriter animation to print out as if you are typing a command after
    the prompt. Results from a "command" appear immediately. 
    """
    def __init__(self, code_box, code_blob):
        """Constructor

        :param code_box: a :class:`CodeBox` widget where the code will be 
                         presented
        :param code: a :class:`Code` object containing code to post
        """
        self.code_box = code_box
        self.code_blob = code_blob

    def setup(self, settings):
        # delay settings
        self.typing_delay = settings['delay'] / 1000
        self.variance = settings['delay_variance']

        # get the chunks of typewriter animation for the first line
        self.chunks = self.code_blob.typewriter_chunks()

        # insert the first chunk from the first line in our CodeBox
        self.current_chunk = 0

        self.state = State.TYPING
        self.code_box.add_line()

    @property
    def delay_until_next_letter(self):
        vary_by = random.randint(0, 2 * self.variance) - self.variance
        return self.typing_delay + (vary_by / 1000)

    def next(self, key):
        if self.current_chunk >= len(self.chunks):
            raise StopIteration

        if self.state == State.TYPING and key is not None:
            # called due to a keypress, we're busy typing so ignore it
            return -1

        if self.state == State.WAITING:
            # got a keypress: start typing
            self.state = State.TYPING

        chunk = self.chunks[self.current_chunk]
        while True:
            if chunk == Animate.NEWLINE:
                self.code_box.add_line()
                self.current_chunk += 1
            elif chunk == Animate.DELAY:
                self.current_chunk += 1
                return self.delay_until_next_letter
            elif chunk == Animate.WAIT:
                self.state = State.WAITING
                self.current_chunk += 1
                return -1
            else:
                # display the markup in the chunk
                self.code_box.set_last_line(chunk)
                self.current_chunk += 1

            if self.current_chunk >= len(self.chunks):
                raise StopIteration

            chunk = self.chunks[self.current_chunk]


class ReplaceTypewriter(AppendTypewriter):
    """Same as :class:`AppendTypewriter` but clears the code box before
    starting the animation.
    """
    def setup(self, settings):
        # Replace is just like Append, but clear the box first
        self.code_box.clear()
        super(ReplaceTypewriter, self).setup(settings)

# =============================================================================

class Insert:
    """Inserts a piece of code at the given line number. Code on the line
    number before the insertion is pushed downards -- i.e. inserting on line 1
    has the new code at the top of the document.
    """
    def __init__(self, code_box, line_number, code_blob):
        """Constructor

        :param code_box: a :class:`CodeBox` widget where the code will be 
            presented
        :param line_number: line number (1-indexed) where code is to be
                            inserted
        :param code: a :class:`Code` object containing code to post
        """
        self.code_box = code_box
        self.code_blob = code_blob
        self.line_number = line_number

    def setup(self, settings):
        line_no = self.line_number
        for line in self.code_blob.lines:
            self.code_box.add_line_at(line_no, line.markup)
            line_no += 1

        self.code_box.fix_line_numbers(self.line_number)

    def next(self, key):
        raise StopIteration

# =============================================================================

class Highlight:
    """Changes the colour attributes of the given line number to be
    highlighted.
    """
    def __init__(self, code_box, line_number, highlight):
        """Constructor

        :param code_box: a :class:`CodeBox` widget where the code will be 
            presented
        :param line_number: line number (1-indexed) where code is to be
                            inserted. Also supports a list of line numbers.
        :param highlight: `True` to turn highlighting on, `False` to turn it off
        """
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
            self.code_box.body.contents[number - 1].set_highlight(
                self.highlight)

        raise StopIteration

# =============================================================================

class StopMovie:
    """If the system is working in movie-mode, this action causes it to leave
    movie mode and go back to being interactive, expecting key presses.
    """
    def __init__(self, screen):
        """Constructor

        :param screen: :class:`Screen` object that controls the playback
        """
        self.screen = screen

    def setup(self, settings):
        pass

    def next(self, key):
        self.screen.movie_mode = -1

        raise StopIteration


class Wait:
    """Action does nothing but wait for a key press"""
    def __init__(self):
        self.called = False

    def setup(self, settings):
        pass

    def next(self, key):
        if not self.called:
            self.called = True
            return -1

        raise StopIteration
