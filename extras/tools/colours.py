#!/usr/bin/env python

import urwid

# ===========================================================================

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

# ===========================================================================

colour_groups = [
    # all colours
    ('black        ', 'white         ', 'brown      ', 'yellow     '),
    ('dark red     ', 'light red     ', 'dark green ', 'light green',), 
    ('dark blue    ', 'light blue    ', 'dark cyan  ', 'light cyan ',),
    ('dark magenta ', 'light magenta ', 'dark gray  ', 'light gray ',),

    # colours from Pygments 
    ('dark cyan    ', 'brown         ', 'dark green ', 'dark magenta'),
    ('dark blue    ', ),
    ('dark blue', ),
]

highlights = [
    'dark gray',
    'light gray',
]

palette = []
mapset = [ {} for h in highlights ]
for group in colour_groups:
    for colour in group:
        cname = colour.rstrip()
        palette.append( (cname, cname, '') )

        for index, highlight in enumerate(highlights):
            hname = f'{cname}_{highlight}_hl'
            palette.append( ( hname, cname, highlight) )
            mapset[index][cname] = hname

# ===========================================================================

# create a Text widget with each colour in the palette
contents = []

#import pudb; pudb.set_trace()
for group in colour_groups:
    text = [(cname.rstrip(), cname) for cname in group]
    contents.append( urwid.Text(text) )

for index, highlight in enumerate(highlights):
    contents.append( urwid.Text(' ') )

    for group in colour_groups:
        text = [(cname.rstrip(), cname) for cname in group]
        contents.append( urwid.AttrMap( urwid.Text(text), mapset[index] ) )


walker = urwid.SimpleListWalker(contents)
box = urwid.ListBox(walker)

loop = urwid.MainLoop(box, palette, unhandled_input=exit_on_q)
loop.run()
