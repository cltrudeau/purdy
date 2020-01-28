#!/usr/bin/env python

import time 

import urwid

# ===========================================================================

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

    if key == 'a':
        global num_walker
        last = len(num_walker)
        top_box.set_focus(last - 1)

# ===========================================================================

class ScrollingIndicator(urwid.Frame):
    def __init__(self):
        self.up = urwid.Text('U')
        self.down = urwid.Text('D')

        # create this Frame with a solid fill in the middle and the up and
        # down Text widgets as the header and footer
        super(ScrollingIndicator, self).__init__(urwid.SolidFill(' '), 
            header=self.up, footer=self.down)

    def set_up(self, is_up, focus):
        if is_up and focus:
            self.up.set_text('▲')
        elif is_up and not focus:
            self.up.set_text('△')
        else:
            self.up.set_text(' ')

    def set_down(self, is_down, focus):
        if is_down and focus:
            self.down.set_text('▼')
        elif is_down and not focus:
            self.down.set_text('▽')
        else:
            self.down.set_text(' ')


class ScrollingListBox(urwid.ListBox):
    def __init__(self, scroll_indicator, *args, **kwargs):
        self.scroll_indicator = scroll_indicator
        super(ScrollingListBox, self).__init__(*args, **kwargs)

    def render(self, size, focus):
        result = super(ScrollingListBox, self).render(size, focus)

        visible = self.ends_visible(size)
        self.scroll_indicator.set_up('top' not in visible, focus)
        self.scroll_indicator.set_down('bottom' not in visible, focus)

        return result


class CodeBox(urwid.Columns):
    def __init__(self, contents):
        self.body = urwid.SimpleListWalker(contents)

        scroller = ScrollingIndicator()
        listbox = ScrollingListBox(scroller, self.body)

        layout = [listbox, (1, scroller)]

        super(CodeBox, self).__init__(layout)

# ===========================================================================

# create ListBox filled with Text widgets containing numbers
contents = [urwid.Text(str(i)) for i in range(1, 51) ]
top_box = CodeBox(contents)

# create ListBox filled with Text widgets containing letters
contents = [urwid.Text(chr(i)) for i in range(65, 95) ]
bottom_box = CodeBox(contents)

# create a Pile with the two list boxes and a divider between them

divider = (3, urwid.Filler(urwid.Divider('-'), valign='top', top=1, bottom=1))

base = urwid.Pile([top_box, divider, bottom_box])

loop = urwid.MainLoop(base, unhandled_input=exit_on_q)
loop.run()
