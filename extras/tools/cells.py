#!/usr/bin/env python
from enum import Enum
import logging
import urwid

logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
    format='%(message)s')
logger = logging.getLogger(__name__)

# ===========================================================================

def handle_key(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

    global manager
    manager.perform(key)

# --------------------------------------------------------------------------
# Control Items

class CellGroup:
    def __init__(self, steps):
        self.steps = steps
        self.index = 0
        self.alarm_handle = None

    def wake_up(self, manager):
        logger.debug('cg.wake_up')
        self.alarm_handle = None
        if self.index < len(self.steps):
            self.render(manager)

    def interrupt(self, manager):
        logger.debug('  interrupted!')
        # interrupted during an animation sequence, remove the timer
        result = manager.loop.remove_alarm(self.alarm_handle)
        logger.debug('  remove_handle:%s', result)

        self.alarm_handle = None
        manager.state = manager.State.ACTIVE
        self.render(manager, skip=True)

    def render(self, manager, skip=False):
        logger.debug('cg.render() skip=%s', skip)
        for x in range(self.index, len(self.steps)):
            logger.debug('   x:%s', x)
            self.index = x
            step = self.steps[x]

            if isinstance(step, Sleep):
                if skip:
                    # in fast-forward mode, do nothing with this Sleep
                    continue
                else:
                    manager.state = manager.State.SLEEPING
                    self.alarm_handle = manager.loop.set_alarm_in(step.time, 
                        manager.window.alarm)
                    logger.debug('   set alarm: %s', self.alarm_handle)
                    self.index += 1
                    break

            step.render_step(manager)

    def undo(self, manager):
        logger.debug('cg.undo()')
        for x in range(self.index, -1, -1):
            logger.debug('   x:%s', x)
            self.index = x
            step = self.steps[x]
            if not isinstance(step, Sleep):
                step.undo_step(manager)


# --------------------------------------------------------------------------

class AnimationManager:
    class State(Enum):
        ACTIVE = 0
        SLEEPING = 1

    def __init__(self, loop, window, walker, cells):
        self.loop = loop
        self.window = window
        self.window.animation_manager = self
        self.walker = walker

        self.state = self.State.ACTIVE

        self.cells = cells
        self.index = -1
        self.size = len(self.cells)

        # set a call-back timer to cause the first animation step
        self.loop.set_alarm_in(0, self.window.alarm)

    def wake_up(self):
        logger.debug('mgr.wake_up()')
        self.state = self.State.ACTIVE
        if self.index == -1:
            logger.debug('  first time')
            self.forward()
        else:
            logger.debug('  alarm')
            self.cells[self.index].wake_up(self)
        
    def perform(self, key):
        if key == 's' and self.state == self.State.SLEEPING:
            self.interrupt()
            return

        if self.state == self.State.SLEEPING:
            # ignore key presses while asleep
            return

        if key == 'right':
            self.forward()
        elif key == 'left':
            self.backward()
        elif key == 's':
            self.fast_forward()

    def forward(self):
        logger.debug('mgr.forward(), index:%s', self.index)
        if self.index + 1 >= self.size:
            return

        self.index += 1
        self.cells[self.index].render(self)

    def fast_forward(self):
        logger.debug('mgr.fast_forward(), index:%s', self.index)
        if self.index + 1 >= self.size:
            return

        self.index += 1
        self.cells[self.index].render(self, skip=True)

    def interrupt(self):
        logger.debug('mgr.interrupt(), index:%s', self.index)
        self.cells[self.index].interrupt(self)

    def backward(self):
        logger.debug('mgr.backward(), index:%s', self.index)
        if self.index <= 0:
            return

        self.cells[self.index].undo(self)
        self.index -= 1

# ---------------------------------------------------------------------------

class AddLine:
    def __init__(self, text):
        self.text = text 

    def render_step(self, manager):
        logger.debug('AddLine.render_step(%s)' % str(self.text))
        manager.walker.contents.append( urwid.Text(self.text) )

    def undo_step(self, manager):
        logger.debug('AddLine.undo_step(%s)' % str(self.text))
        del manager.walker.contents[-1]


class AppendLine:
    def __init__(self, position, text, same_markup=True):
        self.text = text
        self.position = position
        self.undo_state = None
        self.same_markup = same_markup

    def _widget_to_markup(self, widget):
        # urwid.Text.get_text() returns the text and a run length encoding of
        # attributes, need to turn it back into the markup format
        text, attrs = widget.get_text()
        if not attrs:
            # no attributes, return just the text
            return text

        markup = []
        start = 0
        for attr in attrs:
            name = attr[0]
            size = attr[1]
            chunk = text[start:start+size]
            markup.append( (name, chunk) )
            start += size

        return markup

    def _append_markup(self, current, append):
        if isinstance(current, str) and isinstance(append, str):
            # string/string combo
            return current + append

        result = []
        if isinstance(current, list):
            result.extend(current)
        else:
            result = [current, ]

        if isinstance(append, list):
            result.extend(append)
        else:
            result.append(append)

        return result

    def _append_with_same_markup(self, current, text):
        result = []
        if isinstance(current, list):
            result.extend(current)
        else:
            result = [current, ]

        if isinstance(result[-1], str):
            result[-1] = result[-1] + text
        else:
            result[-1] = (result[-1][0], result[-1][1] + text)

        return result

    def render_step(self, manager):
        logger.debug('AppendLine.render_step(%s)' % str(self.text))

        widget = manager.walker.contents[self.position]
        self.undo_state = self._widget_to_markup(widget)

        if self.same_markup:
            new_markup = self._append_with_same_markup(self.undo_state, 
                self.text)
        else:
            new_markup = self._append_markup(self.undo_state, self.text)

        manager.walker.contents[self.position] = urwid.Text(new_markup)

    def undo_step(self, manager):
        logger.debug('AppendLine.undo_step(%s)' % str(self.text))

        manager.walker.contents[self.position] = urwid.Text(self.undo_state )


class InsertLine:
    def __init__(self, position, text):
        self.text = text
        self.position = position

    def render_step(self, manager):
        logger.debug('InsertLine.render_step(%s)' % self.text)

        manager.walker.contents.insert(self.position, urwid.Text(self.text))

    def undo_step(self, manager):
        logger.debug('InsertLine.undo_step(%s)' % self.text)

        del manager.walker.contents[self.position]


class ReplaceLine:
    def __init__(self, position, text):
        self.text = text
        self.position = position
        self.undo_state = None

    def render_step(self, manager):
        logger.debug('ReplaceLine.render_step(%s)' % self.text)

        widget = manager.walker.contents[self.position]
        self.undo_state = widget.get_text()[0]

        manager.walker.contents[self.position] = urwid.Text(self.text)

    def undo_step(self, manager):
        logger.debug('ReplaceLine.undo_step(%s)' % self.text)

        manager.walker.contents[self.position] = urwid.Text(self.undo_state )


class Clear:
    def __init__(self):
        self.undo_state = []

    def render_step(self, manager):
        logger.debug('Clear.render_step()')

        self.undo_state = []
        for widget in manager.walker.contents:
            self.undo_state.append( widget.get_text()[0] )

        manager.walker.contents.clear()

    def undo_step(self, manager):
        logger.debug('Clear.undo_step()')

        for text in self.undo_state:
            manager.walker.contents.append( urwid.Text(text ) )


class Sleep:
    def __init__(self, time):
        self.time = time

# ===========================================================================

class BaseWindow(urwid.ListBox):
    def __init__(self, walker):
        super().__init__(walker)

    def alarm(self, loop, data):
        self.animation_manager.wake_up()

# ===========================================================================

# create a Text widget with each colour in the palette
contents = []

cells = [
    CellGroup([
        AddLine( ('blue', 'one') ),
    ]),
    CellGroup([
        AppendLine(0, ' 111'),
    ]),
    CellGroup([
        AddLine('two'),
        Sleep(3),
        AddLine('three'),
    ]),
    CellGroup([
        AddLine('four'),
        AppendLine(1, ('blue', ' 222'), same_markup=False),
    ]),
    CellGroup([
        InsertLine(2, 'squeeze me'),
        ReplaceLine(0, 'booger'),
    ]),
    CellGroup([
        Clear(),
        AddLine('five'),
        AddLine('six'),
    ]),
]

palette = [
    ('blue', 'dark blue', '', '', '#f00', ''),
]

walker = urwid.SimpleListWalker(contents)
#box = urwid.ListBox(walker)
window = BaseWindow(walker)

loop = urwid.MainLoop(window, unhandled_input=handle_key)
loop.screen.register_palette(palette)

manager = AnimationManager(loop, window, walker, cells)

loop.run()
