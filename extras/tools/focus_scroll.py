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
        num_walker.set_focus(last - 1)

# ===========================================================================

# create ListBox filled with Text widgets containing numbers
contents = [urwid.Text(str(i)) for i in range(1, 51) ]
num_walker = urwid.SimpleListWalker(contents)
top_box = urwid.ListBox(num_walker)

# create ListBox filled with Text widgets containing letters
contents = [urwid.Text(chr(i)) for i in range(65, 95) ]
walker = urwid.SimpleListWalker(contents)
bottom_box = urwid.ListBox(walker)

# create a Pile with the two list boxes and a divider between them

divider = (3, urwid.Filler(urwid.Divider('-'), valign='top', top=1, bottom=1))

base = urwid.Pile([top_box, divider, bottom_box])

loop = urwid.MainLoop(base, unhandled_input=exit_on_q)
loop.run()
