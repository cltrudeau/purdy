#!/usr/bin/env python

import urwid

# ===========================================================================

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

    global loop
    if key == '1':
        loop.screen.set_terminal_properties(colors=16)
        loop.screen.reset_default_terminal_palette()
    elif key == '2':
        loop.screen.set_terminal_properties(colors=256)
        loop.screen.reset_default_terminal_palette()


palette = [
    ('blue-green-b-red-black', 'dark blue', 'dark green', '', '#f00', '#000'),
    ('cyan-black-b-66d-068', 'dark cyan', '', '', '#66d', '#068'),
]

#for colour in colours:
#    palette.append( (colour, '', '', '', colour, '') )

# ===========================================================================

# create a Text widget with each colour in the palette
contents = [] 

for colour in palette:
    contents.append( urwid.Text( (colour[0], colour[0]) ) )

walker = urwid.SimpleListWalker(contents)
box = urwid.ListBox(walker)

loop = urwid.MainLoop(box, palette, unhandled_input=exit_on_q)
loop.screen.set_terminal_properties(colors=256)
loop.run()
