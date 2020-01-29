#!/usr/bin/env python

import time 

import urwid

# ===========================================================================

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

# ===========================================================================

fg_colours = [ 'black', 'dark red', 'dark green', 'brown', 'dark blue', 
    'dark magenta', 'dark cyan', 'light gray', 'dark gray', 'light red', 
    'light green', 'yellow', 'light blue', 'light magenta', 'light cyan', 
    'white', ]

palette = [ (colour, colour, '') for colour in fg_colours ]

palette.append( ('highlight', 'dark gray', 'dark gray') )

# ===========================================================================

# create a Text widget with each colour in the palette
contents = [urwid.Text('*** Starting\n\n'), ]

contents.extend( [urwid.Text((colour, colour)) for colour in fg_colours] )

contents.append( urwid.AttrMap( urwid.Text(('brown', 'brown')), 'highlight' ))

contents.append(urwid.Text('\n\n*** Done'))

walker = urwid.SimpleListWalker(contents)
box = urwid.ListBox(walker)

loop = urwid.MainLoop(box, palette, unhandled_input=exit_on_q)
loop.run()
