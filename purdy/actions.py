"""
Actions (purdy.actions.py)
--------------------------

Actions create the presentation to the user. An action is similar to a
slide in a slide show, except it can both present and change lines of code on
the screen.

All purdy library programs have the following basic structure:

.. code-block:: python

    screen = Screen()
    actions = [ ... ]
    screen.run(actions)


Each presentation must include one or more actions passed to a
:code:`Screen <purdy.ui.Screen>` object. The screen then calls the action's
`setup()` method followed by its `next()` method. The `next()` method does one
of three things: 1) return -1, indicating the screen should wait for the next
key press before calling `next()` again, 2) return >= 0, indicating the screen
should set a timer and call back after the elapsed time (in milliseconds), or
3) raise StopIteration to tell screen this action is complete.

When an action completes, screen looks for the next action in the list, calls
its `setup()` method and then its `next()` method, and the process repeats.

An action has the following structure:

.. code-block:: python

    class SomeAction:

        def setup(self, settings):
            # initial setup, including writing to screen's widgets is done
            # here

        def next(self, key):
            if # done
                raise StopIteration

            elif # wait for key press
                return -1

            else 
                # call me back in 20 ms
                return 20
"""

import random
from enum import Enum

from purdy.content import (Animate, LEXERS, CodeLine, TokenLookup, CodeToken,
    TypewriterChunkifier)

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


class TypewriterAction:
    """Commong base class for actions that use typewriter animation"""
    @property
    def delay_until_next_letter(self):
        vary_by = random.randint(0, 2 * self.variance) - self.variance
        return self.typing_delay + (vary_by / 1000)


class AppendTypewriter(TypewriterAction):
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

class AppendLine:
    """Appends to the given line in the code box. All work is done in the
    setup() phase, does not wait for a key press.  
    """
    def __init__(self, code_box, line_number, text, lexer_name):
        """Constructor

        :param code_box: a :class:`CodeBox` widget where the code will be 
            presented
        :param line_number: line number to append code on (1-indexed)

        :param text: text to append to the line
        """
        self.lexer = LEXERS.get_lexer(lexer_name)
        self.code_box = code_box
        self.line_number = line_number
        self.text = text

    def setup(self, settings):
        # get the current markup and turn it back into just plain text
        markup = self.code_box.get_markup(self.line_number)
        plain = ''.join(part[1] for part in markup)
        plain += self.text

        # create a new CodeLine, re-parsing the text and use that to set the
        # new markup
        markup = CodeLine.parse_factory(plain, self.lexer).markup

        # parser has a habit of randomly adding \n's, remove any
        if markup[-1][1] == '\n':
            markup.pop()

        self.code_box.set_line(self.line_number, markup)

    def next(self, key):
        raise StopIteration


class ReplaceLine(AppendLine):
    """Same as :class:`AppendLine` except the line is replaced
    """
    def setup(self, settings):
        markup = CodeLine.parse_factory(self.text, self.lexer).markup
        self.code_box.set_line(self.line_number, markup)

# -----------------------------------------------------------------------------

class AppendLineTypewriter(TypewriterAction):
    """Appends to the given line in the code box using the typewriter
    animation. 
    """
    def __init__(self, code_box, line_number, text, lexer_name):
        """Constructor

        :param code_box: a :class:`CodeBox` widget where the code will be 
            presented
        :param line_number: line number to append code on (1-indexed)

        :param text: text to append to the line
        """
        self.lexer = LEXERS.get_lexer(lexer_name)
        self.code_box = code_box
        self.line_number = line_number
        self.text = text

    def setup(self, settings):
        # delay settings
        self.typing_delay = settings['delay'] / 1000
        self.variance = settings['delay_variance']

        # get the chunks of typewriter animation for the text
        current_markup = self.code_box.get_markup(self.line_number)
        current_plain = ''.join(part[1] for part in current_markup)
        current_plain = current_plain.rstrip()
        new_text = current_plain + self.text

        tokens = []
        for token_type, text in self.lexer.get_tokens(new_text):
            colour = TokenLookup.get_colouring(token_type)
            tokens.append( CodeToken(token_type, colour, text) )

        # parser has a habit of randomly adding \n's, remove any
        if tokens[-1].text == '\n':
            tokens.pop()

        self.chunks = TypewriterChunkifier().parse(tokens)

        # we don't want to do typewriter for the full line, just for the
        # replacement part, so find the chunk that is equivalent to what is
        # already there and delete everything before it
        for count, chunk in enumerate(self.chunks):
            if isinstance(chunk, Animate):
                continue

            plain_chunk = ''.join(part[1] for part in chunk)
            if plain_chunk == current_plain:
                break

        self.chunks = self.chunks[count:]

        # prepare for the typing sequence
        self.current_chunk = 0
        self.state = State.TYPING

    def next(self, key):
        if self.current_chunk >= len(self.chunks):
            raise StopIteration

        if self.state == State.TYPING and key is not None:
            # called due to a keypress, we're busy typing so ignore it
            return -1

        chunk = self.chunks[self.current_chunk]
        if chunk == Animate.DELAY:
            self.current_chunk += 1
            return self.delay_until_next_letter
        elif isinstance(chunk, Animate):
            # ignore any WAIT or NEWLINE and ask for another callback
            self.current_chunk += 1
            return 0

        markup = self.chunks[self.current_chunk]
        self.code_box.set_line(self.line_number, markup)
        self.current_chunk += 1
        return self.delay_until_next_letter


class ReplaceLineTypewriter(AppendLineTypewriter):
    """Same as :class:`AppendLineTypewriter` but clears the line first
    """
    def setup(self, settings):
        # delay settings
        self.typing_delay = settings['delay'] / 1000
        self.variance = settings['delay_variance']

        # get the chunks of typewriter animation for the text
        tokens = []
        for token_type, text in self.lexer.get_tokens(self.text):
            colour = TokenLookup.get_colouring(token_type)
            tokens.append( CodeToken(token_type, colour, text) )

        # parser has a habit of randomly adding \n's, remove any
        if tokens[-1].text == '\n':
            tokens.pop()

        self.chunks = TypewriterChunkifier().parse(tokens)

        # prepare for the typing sequence
        self.current_chunk = 0
        self.state = State.TYPING

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

# -----------------------------------------------------------------------------

class InsertTypewriter(Insert, TypewriterAction):
    """Same as :class:`Insert` except uses a typewriter animation
    """
    def setup(self, settings):
        # delay settings
        self.typing_delay = settings['delay'] / 1000
        self.variance = settings['delay_variance']

        # get the chunks of typewriter animation for the first line
        self.chunks = self.code_blob.typewriter_chunks()

        # insert the first chunk from the first line in our CodeBox
        self.current_chunk = 0
        self.current_line = self.line_number

        self.code_box.add_line_at(self.line_number)
        self.code_box.fix_line_numbers(self.line_number)

    def next(self, key):
        if self.current_chunk >= len(self.chunks):
            raise StopIteration

        if key is not None:
            # called due to a keypress, we're busy typing so ignore it
            return -1

        chunk = self.chunks[self.current_chunk]
        while True:
            if chunk == Animate.NEWLINE:
                self.current_line += 1
                self.code_box.add_line_at(self.current_line)
                self.code_box.fix_line_numbers(self.current_line)
                self.current_chunk += 1
            elif chunk == Animate.DELAY:
                self.current_chunk += 1
                return self.delay_until_next_letter
            elif chunk == Animate.WAIT:
                # ignore WAIT -- this really shouldn't be used for REPL code
                # anyway (why would you insert in the middle of a console?)
                self.current_chunk += 1
                return 0
            else:
                # display the markup in the chunk
                self.code_box.set_line(self.current_line, chunk)
                self.current_chunk += 1

            if self.current_chunk >= len(self.chunks):
                raise StopIteration

            chunk = self.chunks[self.current_chunk]

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

class EmptySetup:
    """Placeholder action. Can be inherited from for those actions that don't
    need a setup() call
    """
    def setup(self, settings):
        pass

# -----------------------------------------------------------------------------

class StopMovie(EmptySetup):
    """If the system is working in movie-mode, this action causes it to leave
    movie mode and go back to being interactive, expecting key presses.
    """
    def __init__(self, screen):
        """Constructor

        :param screen: :class:`Screen` object that controls the playback
        """
        self.screen = screen

    def next(self, key):
        self.screen.movie_mode = -1

        raise StopIteration


class Wait(EmptySetup):
    """Action does nothing but wait for a key press"""
    def __init__(self):
        self.called = False

    def next(self, key):
        if not self.called:
            self.called = True
            return -1

        raise StopIteration


class Sleep(EmptySetup):
    """Action pauses execution for the given amount of time."""
    def __init__(self, time):
        """Constructor

        :param time: time in milliseconds to sleep for
        """
        self.time = time
        self.called = False

    def next(self, key):
        if not self.called:
            self.called = True
            return self.time

        if self.called and key is not None:
            # got a key press during our sleep, ignore it
            return -1

        # have been called before, so we're done
        raise StopIteration
