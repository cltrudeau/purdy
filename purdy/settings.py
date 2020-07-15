"""
Settings (purdy.settings.py)
============================

Defines the default settings for :class:`purdy.ui.Screen` objects, can be
overridden by passing an altered dictionary into the Screen's constructor. 
"""

settings = {
    # delay between characters appearing on screen (in milliseconds)
    'delay':130,

    # range of random time in milliseconds to change the delay; makes typing
    # look more natural
    'delay_variance':30,

    # movie mode: instead of waiting for key presses, play like a movie, -1
    # disables, otherwise value in milliseconds for delay between played steps
    # (like 'delay' field
    'movie_mode':-1,

    # xterm colour mode, anything but 256 gives 16 colour mode
    'colour':256,

    # if True, stops Screen from running argparse
    'deactivate_args':False,

    # max height for presentation, only works in TUI mode, 0 == no max
    'max_height':0,
}
