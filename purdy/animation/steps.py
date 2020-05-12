#!/usr/bin/env python
"""
Animation Steps
===============

An animation is created through a series of steps that are executed together.
A :class:`.cell.GroupCell` wraps these steps. When the user moves forwards and 
backwards through the animations each cell is rendered or undone. This module 
"""
from copy import deepcopy

from pygments.token import String, Token

from purdy.parser import CodeLine, CodePart, token_is_a, parse_source

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

    @property
    def trunc_lines(self):
        if len(self.lines) == 0:
            return '[]'

        if len(self.lines) == 1:
            return f'[{self.lines[0]}'

        # else len(self.lines) > 1:
        return f'[{self.lines[0]}...]'

    def _test_dict(self):
        d = {
            f'{self.__class__.__name__}': {
                'lines':[line._test_dict() for line in self.lines],
            }
        }

        return d


class PositionTestMixin:
    def _test_dict(self):
        d = {
            f'{self.__class__.__name__}': {
                'lines':[line._test_dict() for line in self.lines],
                'position':self.position,
            }
        }

        return d

# ---------------------------------------------------------------------------
# Line Insertion Steps
# ---------------------------------------------------------------------------

class InsertRows(PositionTestMixin, BaseEditStep):
    def __init__(self, code_box, position, lines):
        super().__init__(code_box, lines)
        self.position = position

    def __str__(self):
        return f'InsertRow("{self.trunc_lines}" @ {self.position})'

    def render_step(self):
        self.code_box.listing.insert_lines(self.position, self.lines)

    def undo_step(self):
        position = self.position
        if position == 0:
            # insert 0 is signal for append, remove last n-lines 
            position = -1 * self.undo_size

        self.code_box.listing.remove_lines(position, self.undo_size)


class Subprocess:
    def __init__(self, code_box, cmd):
        self.code_box = code_box
        self.cmd = cmd

    def _test_dict(self):
        d = {
            'Subprocess': { 'cmd':self.cmd, }
        }

        return d

    def render_step(self):
        import subprocess

        args = self.cmd.strip().split(' ')
        result = subprocess.run(args, capture_output=True, text=True)

        new_lines = []
        for row in result.stdout.split('\n'):
            part = CodePart(Token.Generic.Output, row)
            new_lines.append( CodeLine([part, ], None) )

        self.undo_position = len(self.code_box.listing.lines) + 1
        self.undo_size = len(new_lines)
        self.code_box.listing.insert_lines(0, new_lines)

    def undo_step(self):
        self.code_box.listing.remove_lines(self.undo_position, self.undo_size)

# ---------------------------------------------------------------------------
# Line Editing Steps
# ---------------------------------------------------------------------------

class ReplaceRows(PositionTestMixin, BaseEditStep):
    def __init__(self, code_box, position, lines):
        super().__init__(code_box, lines)
        self.position = position

    def __str__(self):
        return f'ReplaceRow("{self.trunc_lines}" @ {self.position})'

    def render_step(self):
        self.undo_lines = self.code_box.listing.copy_lines(self.position,
            self.undo_size)

        for count, line in enumerate(self.lines):
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

    def _test_dict(self):
        d = {
            'SuffixRow': {
                'position':self.position,
                'source':self.source,
                'cursor':self.cursor,
            }
        }

        return d

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
        line = deepcopy(self.code_box.listing.lines[self.position - 1])
        self.undo_line = line

        token = line.parts[-1][0]
        if self._inside_string(line):
            # inside a multi-line string, don't reparse, just append
            parts = deepcopy(line.parts)
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

    def _test_dict(self):
        d = {
            'RemoveRows': {
                'position':self.position,
                'num':self.num,
            }
        }

        return d

    def render_step(self):
        self.undo_lines = []
        for x in range(0, self.num):
            line = self.code_box.listing.lines[x + self.position - 1]
            undo_line = deepcopy(line)
            self.undo_lines.append(undo_line)

        self.code_box.listing.remove_lines(self.position, self.num)

    def undo_step(self):
        self.code_box.listing.insert_lines(self.position, self.undo_lines)


class Clear:
    def __init__(self, code_box):
        self.code_box = code_box

    def _test_dict(self):
        d = {
            'Clear': {}
        }

        return d

    def render_step(self):
        self.undo_lines = []
        for line in self.code_box.listing.lines:
            undo_line = deepcopy(line)
            self.undo_lines.append(undo_line)

        self.code_box.listing.clear()

    def undo_step(self):
        self.code_box.listing.insert_lines(0, self.undo_lines)

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

    def _test_dict(self):
        d = {
            'HighlightLines': {
                'numbers':str(self.numbers),
                'highlight_on':self.highlight_on,
            }
        }

        return d

    def _set_highlight(self, highlight_value):
        for num in self.numbers:
            self.code_box.listing.set_highlight(highlight_value, num, num)

    def render_step(self):
        self._set_highlight(self.highlight_on)

    def undo_step(self):
        self._set_highlight(not self.highlight_on)


class FoldLines:
    def __init__(self, code_box, position, end):
        self.code_box = code_box
        self.position = position
        self.end = end

    def __str__(self):
        return f'FoldLines({self.position}, {self.end})'

    def _test_dict(self):
        d = {
            'FoldLines':{
                'position':self.position,
                'end':self.end,
            }
        }
        return d

    def render_step(self):
        self.undo_lines = []

        start = self.position - 1
        last = self.end
        if self.end == -1:
            last = len(self.code_box.listing.lines)

        for line in self.code_box.listing.lines[start:last]:
            undo_line = deepcopy(line)
            self.undo_lines.append(undo_line)

        self.code_box.listing.fold_lines(self.position, last)

    def undo_step(self):
        self.code_box.listing.insert_lines(self.position, self.undo_lines)
        self.code_box.listing.remove_lines(self.position + len(self.undo_lines),
            1)

# ---------------------------------------------------------------------------
# Control Steps
# ---------------------------------------------------------------------------

class Sleep:
    def __init__(self, time):
        self.time = time

    def __str__(self):
        return f'Sleep("{self.time}")'

    def _test_dict(self):
        # Do not serialize the time parameter, it is random and will fail the
        # next comparison
        d = {
            'Sleep': {}
        }

        return d


class CellEnd:
    pass


class Transition:
    def __init__(self, code_box, code):
        self.code_box = code_box
        self.code = code


class StopMovieException(Exception):
    pass


class StopMovie:
    def _test_dict(self):
        d = {
            'StopMovie': {},
        }

        return d
    def render_step(self):
        raise StopMovieException()

    def undo_step(self):
        pass
