#!/usr/bin/env python
"""
Animation Steps
---------------

An animation is created through a series of steps that are executed together.
A :class:`Cell` wraps these steps. When the user moves forwards and backwards
through the animations each Cell is rendered or undone. This module contains
the Cell and the steps that can be contained within it.
"""
from copy import copy

from pygments.token import String, Token

from purdy.parser import CodeLine, CodePart, token_is_a, parse_source

# ===========================================================================
# Cell Management
# ===========================================================================

class Cell:
    @classmethod
    def group_steps_into_cells(cls, steps):
        """Actions create multiple steps possibly with cell breaks between
        them. This method takes a list of steps and returns a list of Cell
        objects, grouping the steps by break marker

        :param steps: a list of steps
        :returns: a list of Cell objects
        """
        cells = []
        cell = Cell()
        for step in steps:
            if isinstance(step, CellEnd):
                cells.append(cell)
                cell = Cell()
            else:
                cell.steps.append(step)

        if len(cell.steps) > 0:
            cells.append(cell)

        return cells

    def __init__(self):
        self.steps = []
        self.index = 0
        self.typewriter_alarm_handle = None

    def __str__(self):
        step_string = ','.join([str(step) for step in self.steps])
        return 'Cell(steps=[' + step_string + '])'

    def typewriter_wake_up(self, manager):
        self.typewriter_alarm_handle = None
        if self.index < len(self.steps):
            self.render(manager)

    def interrupt(self, manager):
        # interrupted during an animation sequence, remove the timer
        manager.screen.loop.remove_alarm(self.typewriter_alarm_handle)

        self.typewriter_alarm_handle = None
        manager.state = manager.State.ACTIVE
        self.render(manager, skip=True)

    def render(self, manager, skip=False):
        if len(self.steps) == 0:
            # badly formed action sequences that result in an empty cell would
            # cause a crash, just do nothing
            return

        for x in range(self.index, len(self.steps)):
            self.index = x
            step = self.steps[x]

            if isinstance(step, Sleep):
                if skip:
                    # in fast-forward mode, do nothing with this Sleep
                    continue
                else:
                    manager.state = manager.State.SLEEPING
                    loop = manager.screen.loop
                    self.typewriter_alarm_handle = loop.set_alarm_in(step.time, 
                            manager.screen.base_window.animation_alarm)
                    self.index += 1
                    return

            try:
                step.render_step()
            except StopMovieException:
                manager.screen.movie_mode = -1

    def undo(self, manager):
        if len(self.steps) == 0:
            # badly formed action sequences that result in an empty cell would
            # cause a crash, just do nothing
            return

        # if we rendered everything and the last call was a Sleep, the index
        # may be past our list bounds
        if self.index >= len(self.steps):
            self.index = len(self.steps) - 1

        for x in range(self.index, -1, -1):
            self.index = x
            step = self.steps[x]
            if not isinstance(step, Sleep):
                step.undo_step()

# ===========================================================================
# Animation Steps
# ===========================================================================

class BaseEditStep:
    def __init__(self, code_box, lines):
        self.code_box = code_box
        self.lines = lines

        if isinstance(lines, CodeLine):
            # if lines is a single item, put it in a list for consistency
            self.lines = [lines, ]

        self.undo_size = len(self.lines)

# ---------------------------------------------------------------------------
# Line Insertion Steps
# ---------------------------------------------------------------------------

class AddRows(BaseEditStep):
    def __str__(self):
        return f'AddRows("{self.lines}")'

    def render_step(self):
        self.undo_position = len(self.code_box.listing.lines) + 1
        self.code_box.listing.append_lines(self.lines)

    def undo_step(self):
        self.code_box.listing.remove_lines(self.undo_position, self.undo_size)


class InsertRows(BaseEditStep):
    def __init__(self, code_box, position, lines):
        super().__init__(code_box, lines)
        self.position = position

    def __str__(self):
        return f'InsertRow("{self.lines}" @ {self.position})'

    def render_step(self):
        self.code_box.listing.insert_lines(self.position, self.lines)

    def undo_step(self):
        self.code_box.listing.remove_lines(self.position, self.undo_size)

# ---------------------------------------------------------------------------
# Line Editing Steps
# ---------------------------------------------------------------------------

class ReplaceRows(BaseEditStep):
    def __init__(self, code_box, position, lines):
        super().__init__(code_box, lines)
        self.position = position

    def __str__(self):
        return f'ReplaceRow("{self.lines}" @ {self.position})'

    def render_step(self):
        self.undo_lines = []
        for count, line in enumerate(self.lines):
            index = self.position - 1 + count

            undo_line = copy(self.code_box.listing.lines[index])
            self.undo_lines.append(undo_line)

            self.code_box.listing.replace_line(self.position + count, line)

    def undo_step(self):
        for count, line in enumerate(self.undo_lines):
            self.code_box.listing.replace_line(self.position + count, line)


class SuffixRow(BaseEditStep):
    def __init__(self, code_box, position, source, cursor=False):
        self.code_box = code_box
        self.position = position
        self.source = source
        self.cursor = cursor

    def __str__(self):
        return f'SuffixRow("{self.source}" @ {self.position})'

    def _inside_string(self, line):
        # Returns True if appending something to the end of this line will be
        # appending inside of a string
        last_token = line.parts[-1][0]
        if not token_is_a(last_token, String):
            return False

        # token is a String, check if multi-line
        try:
            # (position is 1-indexed, so next line in 0-index is itself)
            next_line = self.code_box.listing.lines[self.position]
        except IndexError:
            # nothing after this, so it must be a closed string
            return False

        last_token_next_line = next_line.parts[0][0]
        if not token_is_a(last_token_next_line, String):
            # next token is not a string, must be a closed string
            return False

        # if you get here we are a String and we have a String as the next
        # line, this could be because we're inside a multi-line string or
        # because the code has two doc strings back-to-back, this is the worst
        # case scenario, loop through the code and count String openers that
        # are the same as this one, if odd number, we're inside a string
        inside = False
        for line in self.code_box.listing.lines[0:self.position]:
            for part in line.parts:
                if part.token == last_token:
                    inside = not inside

        return inside

    def render_step(self):
        line = copy(self.code_box.listing.lines[self.position - 1])
        self.undo_line = line

        token = line.parts[-1][0]
        if self._inside_string(line):
            # inside a multi-line string, don't reparse, just append
            parts = copy(line.parts)
            parts[-1] = CodePart(token, parts[-1].text + self.source)
            replace_line = CodeLine(parts, line.lexer)
        else:
            # not inside a string
            if token_is_a(token, String):
                # last token is a string, parse the source and append
                source_line = parse_source(self.source, line.lexer)[0]
                new_parts = line.parts + source_line.parts
                replace_line = CodeLine(new_parts, line.lexer)
            else:
                # last token isn't a string, reparse the whole line
                text = line.text + self.source
                replace_line = parse_source(text, line.lexer)[0]

        if self.cursor:
            replace_line.parts.append( CodePart(Token, '\u2588') )

        self.code_box.listing.replace_line(self.position, replace_line)

    def undo_step(self):
        self.code_box.listing.replace_line(self.position, self.undo_line)


class RemoveRows:
    def __init__(self, code_box, position, num=1):
        self.code_box = code_box
        self.position = position
        self.num = num

    def __str__(self):
        return f'RemoveRows({self.position} for {self.num})'

    def render_step(self):
        self.undo_lines = []
        for x in range(0, self.num):
            line = self.code_box.listing.lines[x + self.position - 1]
            undo_line = copy(line)
            self.undo_lines.append(undo_line)

        self.code_box.listing.remove_lines(self.position, self.num)

    def undo_step(self):
        self.code_box.listing.insert_lines(self.position, self.undo_lines)


class Clear:
    def __init__(self, code_box):
        self.code_box = code_box

    def render_step(self):
        self.undo_lines = []
        for line in self.code_box.listing.lines:
            undo_line = copy(line)
            self.undo_lines.append(undo_line)

        self.code_box.listing.clear()

    def undo_step(self):
        self.code_box.listing.insert_lines(1, self.undo_lines)

# ---------------------------------------------------------------------------
# Presentation Steps
# ---------------------------------------------------------------------------

class HighlightLines:
    def __init__(self, code_box, numbers, highlight_on):
        self.code_box = code_box
        if isinstance(numbers, int):
            self.numbers = [numbers, ]
        else:
            self.numbers = numbers
        self.highlight_on = highlight_on

    def __str__(self):
        return f'HighlightLines("{self.numbers}", {self.highlight_on})'

    def _set_highlight(self, highlight_value):
        for num in self.numbers:
            self.code_box.listing.set_highlight(highlight_value, num, num)

    def render_step(self):
        self._set_highlight(self.highlight_on)

    def undo_step(self):
        self._set_highlight(not self.highlight_on)

# ---------------------------------------------------------------------------
# Control Steps
# ---------------------------------------------------------------------------

class Sleep:
    def __init__(self, time):
        self.time = time

    def __str__(self):
        return f'Sleep("{self.time}")'


class CellEnd:
    pass


class StopMovieException(Exception):
    pass


class StopMovie:
    def render_step(self):
        raise StopMovieException()

    def undo_step(self):
        pass
