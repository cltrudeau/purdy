"""
Actions
=======

Library users specify a series of actions that turn into the presentation
animations in the Urwid client.  An action is similar to a slide in a slide
show, except it can both present and change lines of code on the screen.

All purdy library programs have the following basic structure:

.. code-block:: python

    screen = Screen(...)
    actions = [ ... ]
    screen.run(actions)

Each action gets translated into a series of steps defined in the
:mod:`purdy.animation` module.
"""
import random
from copy import deepcopy

from pygments.token import Generic, Token

from purdy.animation import steps as steplib
from purdy.content import Code
from purdy.parser import CodePart, CodeLine, parse_source, token_is_a
from purdy.scribe import range_set_to_list

#import logging
#logging.basicConfig(filename='debug.log', level=logging.DEBUG)
#logger = logging.getLogger()

# =============================================================================

def condense(value):
    if not value:
        return ''

    content = deepcopy(value)
    if len(content) >= 20:
        content = content[0:17] + '...'

    return content

# =============================================================================
# Single Code Blob Actions
# =============================================================================

class Insert:
    """Inserts the content of a :class:`purdy.content.Code` object to a
    specified line in a :class:`purdy.ui.CodeBox`. Pushes content down,
    inserting at "1" is the beginning of the list. Position is 1-indexed

    :param code_box: the :class:`purdy.ui.CodeBox` instance to insert code
                     into

    :param position: line number to insert code at. Position is 1-indexed.
                     Content is pushed down, so a value of "1" inserts at the
                     beginning. Negative indicies are supported. A value of
                     "0" will append the code to the bottom.

    :param code: a :class:`purdy.content.Code` object containing the source
                 code to insert, or a string. Strings are treated as text
                 without highlighting.

    :param pauses: optional list of :class:`purdy.actions.Pause` objects that
                   specify where to insert pauses in the output
    """
    def __init__(self, code_box, position, code, pauses=[]):
        self.code_box = code_box
        self.position = position
        self.pauses = pauses

        if isinstance(code, str):
            self.code = Code(text=code, lexer_name="none")
        else:
            self.code = code

    def __str__(self):
        content = condense(self.code.source)
        return f'actions.Insert({self.position}, "{content}")'

    def steps(self):
        lines = parse_source(self.code.source, self.code.lexer)
        if not self.pauses:
            # No pauses to insert, insert it all
            steps = [steplib.InsertRows(self.code_box, self.position, lines), ]
        else:
            start = 0
            steps = []

            for count, pause in enumerate(self.pauses):
                # Insert everything up to the pause
                subset = lines[start:pause.line_no]
                offset = self.position + count
                step = steplib.InsertRows(self.code_box, offset, subset)
                steps.append(step)

                # Do the pause by inserting a sleep step
                steps.append(steplib.Sleep(pause.duration))

                start += len(subset)

            if start < len(lines):
                # Insert the remainder
                subset = lines[start:]
                offset = self.position + count
                step = steplib.InsertRows(self.code_box, offset, subset)
                steps.append(step)

        return steps


class Append(Insert):
    """Adds the content of a :class:`purdy.content.Code` object to the end of
    a :class:`purdy.ui.CodeBox`.

    :param code_box: the :class:`purdy.ui.CodeBox` instance to insert code
                     into

    :param code: a :class:`purdy.content.Code` object containing the source
                 code to insert, or a string. Strings are treated as text
                 without highlighting.

    :param pauses: optional list of :class:`purdy.actions.Pause` objects that
                   specify where to insert pauses in the output
    """
    def __init__(self, code_box, code, pauses=[]):
        super().__init__(code_box, 0, code, pauses)

    def __str__(self):
        content = condense(self.code.source)
        return f'actions.Append("{content}")'


class Replace:
    """Replaces one or more lines of a :class:`purdy.ui.CodeBox` using the
    content of a :class:`purdy.content.Code` object. This action attempts to
    overwrite using the number of lines in the :class:`purdy.content.Code`
    object passed in, it is up to you to make sure there is enough space in
    your CodeBox.

    :param code_box: the :class:`purdy.ui.CodeBox` instance where the code is
                     to be replaced

    :param position: line number to replace the code at. Position is 1-indexed.
                     Negative indicies are supported.

    :param code: a :class:`purdy.content.Code` object containing the source
                 code to insert.
    """
    def __init__(self, code_box, position, code):
        self.code_box = code_box
        self.code = code
        self.position = position

    def __str__(self):
        content = condense(self.code.source)
        return f'actions.Replace({self.position}, "{content}")'

    def steps(self):
        lines = parse_source(self.code.source, self.code.lexer)
        steps = [steplib.ReplaceRows(self.code_box, self.position, lines), ]

        return steps


class Remove:
    """Removes one or more lines of a :class:`purdy.ui.CodeBox`.

    :param code_box: the :class:`purdy.ui.CodeBox` instance where the code is
                     to be replaced

    :param position: line number to replace the code at. Position is 1-indexed.
                     Negative indicies are supported.

    :param size: number of lines to remove.
    """
    def __init__(self, code_box, position, size):
        self.code_box = code_box
        self.position = position
        self.size = size

    def __str__(self):
        return f'actions.Remove({self.position}, "{self.size}")'

    def steps(self):
        return [steplib.RemoveRows(self.code_box, self.position, self.size), ]


class Clear:
    """Clears the contents of a :class:`purdy.ui.CodeBox`.

    :param code_box: the :class:`purdy.ui.CodeBox` instance where the code is
                     to be replaced
    """
    def __init__(self, code_box):
        self.code_box = code_box

    def __str__(self):
        return 'actions.Clear()'

    def steps(self):
        return [steplib.Clear(self.code_box), ]

# =============================================================================
# Source Based Actions
# =============================================================================

class Suffix:
    """Adds the provided text to the end of an existing line in a
    :class:`purdy.ui.CodeBox`.

    :param code_box: the :class:`purdy.ui.CodeBox` instance where the code is
                     to be appended

    :param position: line number to replace the code at. Position is 1-indexed.
                     Negative indicies are supported.

    :param source: string containing content to append to the line
    """
    def __init__(self, code_box, position, source):
        self.code_box = code_box
        self.position = position
        self.source = source

    def __str__(self):
        return f'actions.Suffix({self.position}, "{self.source}")'

    def steps(self):
        return [steplib.SuffixRow(self.code_box, self.position, self.source), ]


class Shell:
    """Runs a shell command via subprocess. Does not display the command
    (you're better off using a typewriter command to show it, then use this to
    spit out the results).  Command and results are added to the
    :class:`purdy.ui.CodeBox`.

    :param code_box: the :class:`purdy.ui.CodeBox` instance where the code is
                     to be appended

    :param cmd: string containing the shell command and its paramters.
                Example: ``ls -la``.
    """
    def __init__(self, code_box, cmd):
        self.code_box = code_box
        self.cmd = cmd

    def __str__(self):
        return f'actions.Suffix("{self.cmd}")'

    def steps(self):
        return [steplib.Subprocess(self.code_box, self.cmd), ]

# =============================================================================
# Typewriter Actions
# =============================================================================

class TypewriterBase:
    continuous = [Generic.Prompt, Generic.Output, Generic.Traceback]

    @property
    def delay_until_next_letter(self):
        typing_delay = self.code_box.screen.settings['delay'] / 1000
        variance = self.code_box.screen.settings['delay_variance']

        vary_by = random.randint(0, 2 * variance) - variance
        return typing_delay + (vary_by / 1000)


class TypewriterStep(TypewriterBase):
    def _line_to_steps(self, line, insert_pos, replace_pos):
        steps = []

        # --- Skip animation for "output" content
        first_token = line.parts[0].token
        is_console = self.code.lexer.is_console

        if is_console and not token_is_a(first_token, Generic.Prompt):
            # in console mode only lines with prompts get typewriter
            # animation, everything else is just added directly
            return [steplib.InsertRows(self.code_box, insert_pos, line), ]

        # --- Typewriter animation
        # insert a blank row first with contents of line changing what is on
        # it as animation continues
        dummy_parts = [CodePart(Token, ''), ]
        row_line = CodeLine(dummy_parts, self.code.lexer)
        step = steplib.InsertRows(self.code_box, insert_pos, row_line)
        steps.append(step)

        current_parts = []
        num_parts = len(line.parts)
        for count, part in enumerate(line.parts):
            if part.token in self.continuous:
                # part is a chunk that gets output all together, replace the
                # dummy line with the whole contents
                current_parts.append(part)
                row_line = CodeLine(deepcopy(current_parts), self.code.lexer)
                step = steplib.ReplaceRows(self.code_box, replace_pos, row_line)
                steps.append(step)

                if part.token == Generic.Prompt:
                    # stop animation if this is a prompt, wait for keypress
                    steps.append( steplib.CellEnd() )
            elif count == 0 and token_is_a(part.token, Token.Text) and (
                    part.text.rstrip() == ''):
                # first token is leading whitespace, don't animate it, just
                # insert it
                current_parts.append(part)
                row_line = CodeLine(deepcopy(current_parts), self.code.lexer)
                step = steplib.ReplaceRows(self.code_box, replace_pos, row_line)
                steps.append(step)
            else:
                new_part = CodePart(part.token, '')
                current_parts.append(new_part)

                typewriter = ''
                for letter in part.text:
                    typewriter += letter
                    new_part = CodePart(part.token, typewriter)
                    current_parts[-1] = new_part
                    output_parts = deepcopy(current_parts)

                    # If not last step in animation, add a cursor to the line
                    is_last_part = (count + 1 == num_parts)
                    is_last_letter = (len(typewriter) == len(part.text))
                    if not (is_last_part and is_last_letter):
                        output_parts.append( CodePart(Token, '\u2588') )

                    row_line = CodeLine(output_parts, self.code.lexer)
                    step = steplib.ReplaceRows(self.code_box, replace_pos,
                        row_line)
                    steps.append(step)

                    steps.append(steplib.Sleep(self.delay_until_next_letter))

        return steps


    def steps(self):
        steps = []
        pauses = {p.line_no:p for p in self.pauses}

        lines = parse_source(self.code.source, self.code.lexer)
        for count, line in enumerate(lines):
            if self.position == 0:
                # Append to end
                line_steps = self._line_to_steps(line, 0, -1)
            else:
                # Append to position
                spot = self.position + count
                line_steps = self._line_to_steps(line, spot, spot)

            if count in pauses:
                # Processed line is supposed to have a Pause after it
                steps.append(steplib.Sleep(pauses[count].duration))

            steps.extend(line_steps)

        return steps


class AppendTypewriter(TypewriterStep):
    """Adds the content of a :class:`purdy.content.Code` object to a
    :class:`purdy.ui.CodeBox` using the typewriter animation.

    :param code_box: the :class:`purdy.ui.CodeBox` instance to append code
                     into

    :param code: a :class:`purdy.content.Code` object containing the source
                 code to insert.

    :param pauses: optional list of :class:`purdy.actions.Pause` objects that
                   specify where to insert pauses in the output
    """

    def __init__(self, code_box, code, pauses=[]):
        self.code_box = code_box
        self.code = code
        self.position = 0
        self.pauses = pauses

    def __str__(self):
        content = condense(self.code.source)
        return f'actions.AppendTypewriter("{content}")'


class InsertTypewriter(TypewriterStep):
    """Inserts the contents of a :class:`purdy.content.Code` object at the
    given position using the typewriter animation.

    :param code_box: the :class:`purdy.ui.CodeBox` instance to append code
                     into

    :param position: line number to insert the code at. Position is 1-indexed.

    :param code: a :class:`purdy.content.Code` object containing the source
                 code to insert.

    :param pauses: optional list of :class:`purdy.actions.Pause` objects that
                   specify where to insert pauses in the output
    """
    def __init__(self, code_box, position, code, pauses=[]):
        if position < 0:
            raise AttributeError(
                'Negative indicies are not supported for this action')

        self.code_box = code_box
        self.code = code
        self.position = position
        self.pauses = pauses

    def __str__(self):
        content = condense(self.code.source)
        return f'actions.InsertTypewriter({self.position}, "{content}")'


class SuffixTypewriter(TypewriterBase):
    """Adds the provided text to the end of an existing line in a
    :class:`purdy.ui.CodeBox` using a typewriter animation.

    :param code_box: the :class:`purdy.ui.CodeBox` instance to append code
                     into

    :param position: line number to insert the code at. Position is 1-indexed.
                     Negative indicies are supported.

    :param source: a string to be appended to the given line
    """
    def __init__(self, code_box, position, source):
        self.code_box = code_box
        self.position = position
        self.source = source
        self.pauses = []

    def __str__(self):
        return f'actions.SuffixTypewriter({self.position}, "{self.source}")'

    def steps(self):
        steps = []
        for count, letter in enumerate(self.source):
            cursor = False
            if count + 1 != len(self.source):
                cursor = True

            steps.extend([
                steplib.SuffixRow(self.code_box, self.position, letter, cursor),
                steplib.Sleep(self.delay_until_next_letter),
            ])

        return steps


class AppendPrompt(TypewriterBase):
    """This action is used to show a prompt and its response. It appends the
    content of a :class:`purdy.content.Code` object to a
    :class:`purdy.ui.CodeBox` as a prompt, waits for the 'right arrow' key,
    then uses the typewriter animation to add the response to the same line.

    :param code_box: the :class:`purdy.ui.CodeBox` instance to append code
                     into

    :param code: a :class:`purdy.content.Code` object containing the prompt
                 code to insert.

    :param response: text to place after the prompt
    """
    def __init__(self, code_box, code, response):
        self.code_box = code_box
        self.code = code
        self.response = response
        self.pauses = []

    def __str__(self):
        prompt = condense(self.code.source)
        response = condense(self.response)

        return f'actions.AppendPrompt({prompt}, {response}")'

    def steps(self):
        # Insert the prompt, then wait
        lines = parse_source(self.code.source, self.code.lexer)
        steps = [steplib.InsertRows(self.code_box, 0, lines), ]
        steps.append(steplib.CellEnd())

        # Insert the response
        for count, letter in enumerate(self.response):
            cursor = False
            if count + 1 != len(self.response):
                cursor = True

            steps.extend([
                steplib.SuffixRow(self.code_box, -1, letter, cursor),
                steplib.Sleep(self.delay_until_next_letter),
            ])

        return steps

# =============================================================================
# Presentation Actions
# =============================================================================

class Highlight:
    """Cause one or more lines of code to have highlighting turned on or off

    :param code_box: :class:`purdy.ui.CodeBox` to perform on

    :param spec: either a string containing comma separated and/or hyphen
                 separated integers (e.g. "1,3,7-9") or a list of integers
                 specifying the lines in the code box to highlight. Line
                 numbers are 1-indexed

    :param highlight_on: True to turn highligthing on, False to turn it off
    """
    def __init__(self, code_box, spec, highlight_on):
        self.code_box = code_box
        self.highlight_on = highlight_on

        if isinstance(spec, str):
            self.numbers = range_set_to_list(spec)
        else:
            self.numbers = spec

    def __str__(self):
        return f'actions.Highlight({self.numbers}, {self.highlight_on})'

    def steps(self):
        return [steplib.HighlightLines(self.code_box, self.numbers,
            self.highlight_on) ]


class HighlightChain:
    """A common pattern with highlighting lines is to turn a highlight on for
    some set of lines, then turn it off and turn it on for more lines. This is
    a convenience wrapper to the :class:`Highlight` action, turning items on
    and off in series.

    :param code_box: :class:`purdy.ui.CodeBox` to perform series of highlight on

    :param spec_list: a list of highlight specs (see :class:`Highlight` for
                      details on a spec)
    """
    def __init__(self, code_box, spec_list):
        self.code_box = code_box
        self.spec_list = spec_list

    def __str__(self):
        return f'actions.HighlightChain({self.spec_list})'

    def steps(self):
        all_steps = []
        previous_numbers = None
        for spec in self.spec_list:
            if isinstance(spec, str):
                numbers = range_set_to_list(spec)
            else:
                numbers = spec

            if previous_numbers:
                all_steps.append( steplib.HighlightLines(self.code_box,
                    previous_numbers, False) )

            all_steps.extend([
                steplib.HighlightLines(self.code_box, numbers, True),
                steplib.CellEnd()
            ])

            previous_numbers = numbers

        if previous_numbers:
            all_steps.append( steplib.HighlightLines(self.code_box,
                previous_numbers, False) )

        return all_steps


class Fold:
    """Folds code by replacing one or more lines with a vertical elipses
    symbol.


    :param code_box: the :class:`purdy.ui.CodeBox` instance to modify

    :param position: line number to begin the fold at. Position is 1-indexed.

    :param end: line number to finish the folding at, inclusive. A value of -1
                can be used to fold to the end of the box. Defaults to -1.
    """
    def __init__(self, code_box, position, end=-1):
        self.code_box = code_box
        self.position = position
        self.end = end
        if end != -1 and end < position:
            raise AttributeError((f'Ending line number ({end}) must be '
                f'larger than starting number ({position})'))

    def __str__(self):
        return f'actions.Fold({self.position}, {self.end})'

    def steps(self):
        return [steplib.FoldLines(self.code_box, self.position, self.end)]

# =============================================================================
# Control Actions
# =============================================================================

class Wait:
    """Causes the animations to wait for a `right arrow` key press before
    continuing.
    """
    def __str__(self):
        return 'actions.Wait()'

    def steps(self):
        return [steplib.CellEnd(), ]


class StopMovie:
    """Causes the presentation :class:`purdy.ui.Screen` to exit movie mode"""
    def __str__(self):
        return 'actions.StopMovie()'

    def steps(self):
        return [steplib.StopMovie(), ]


class Transition:
    """Replaces the contents of a :class:`purdy.ui.CodeBox` with new content,
    doing a wipe animation from top to bottom. Only one of `code` or
    `code_box_to_copy` should be given, both can be blank to transition to an
    empty screen.

    :param code_box: the :class:`purdy.ui.CodeBox` instance to perform the
                     transition on

    :param code: a :class:`purdy.content.Code` object containing the source
                 code replacing the existing content. Should not be used at
                 the same time as code_box_to_copy parameter.

    :param code_box_to_copy: a code box containing rendered code to copy into
                             this one to display. This is typically a
                             :class:`VirtualCodeBox`. Should not be used at
                             the same time as code parameter.
    """
    def __init__(self, code_box, code=None, code_box_to_copy=None):
        self.code_box = code_box
        self.code = code
        self.code_box_to_copy = code_box_to_copy

    def __str__(self):
        code_content = ''
        if self.code:
            code_content = condense(self.code.source)

        copy_content = ''
        if self.code_box_to_copy:
            lines = [str(line) for line in self.code_box_to_copy.listing.lines]
            copy_content = condense('\n'.join(lines))

        return f'actions.Transition("{code_content}", "{copy_content}")'

    def steps(self):
        return [steplib.Transition(self.code_box, self.code,
            self.code_box_to_copy), ]


class Sleep:
    """Causes animations to pause for the given amount of time. Note that this
    action happens within a cell, so is considered part of the group of
    animation steps done together. For example if Append + Sleep + Append is
    part of the same cell it is all done/undone together.

    :param time: Either the amount of time to sleep in seconds (ints and 
                 floats supported), or a tuple containing a pair of times
                 specifying the range of a random value to sleep.

    """
    def __init__(self, time):
        self.time = time

    def __str__(self):
        return 'actions.Sleep'

    def steps(self):
        return [steplib.Sleep(self.time), ]


class RunFunction:
    r"""Calls the function passed in, allowing the execution of code during the
    playing of actions.

    :param fn: function to be called
    :param undo: function to be called when this Action is undone, can be None
    :param \*args: any remaining arguments are passed to the functions when
                   they are called
    :param \*\*kwargs: any remaining arguments are passed to the
                            functions when they are called
    """
    def __init__(self, fn, undo, *args, **kwargs):
        self.fn = fn
        self.undo = undo
        self.fn_args = args
        self.fn_kwargs = kwargs

    def __str__(self):
        return 'actions.RunFunction'

    def steps(self):
        return [steplib.RunFunction(self.fn, self.undo, *self.fn_args,
            **self.fn_kwargs), ]


class Section:
    """Marker for the beginning of a section. In the TUI you can skip to the
    next section marker using "S"."""

    def __str__(self):
        return 'actions.Section()'

    def steps(self):
        return [steplib.SectionBreak(), ]


class Pause:
    """Used by some actions to indicate a delay between output lines.

    :param line_no: line in block to insert pause after. Note that this does
        not differentiate between code and output, just lines in a block
    :param duartion: time in seconds to delay (ints and floats supported)
    """

    def __init__(self, line_no, duration):
        self.line_no = line_no
        self.duration = duration

    def __str__(self):
        return f'actions.Pause(line={self.line_no}, amt={self.duration})'
