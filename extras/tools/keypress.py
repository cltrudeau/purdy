#!/usr/bin/env python
import urwid

# ===========================================================================

def handle_key(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

    global walker
    walker.contents.append( urwid.Text(key) )

# ===========================================================================

contents = []

walker = urwid.SimpleListWalker(contents)
box = urwid.ListBox(walker)

loop = urwid.MainLoop(box, unhandled_input=handle_key)
loop.run()
