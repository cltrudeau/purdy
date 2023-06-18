# purdy.py
#
# Command for using the purdy TUI with a file

import argparse

from purdy.cmdline.utils import common_arg, filename_arg
from purdy.content import Code
from purdy.tui.screen import SimpleScreen

# ===========================================================================

DESCRIPTION = """This is a TUI colourized file viewer with two modes, either
showing the whole file, or presenting it as if it is being typed line by line
as a slide-show. Colourization of the file is based on a limited number of
pygments lexers.  A list of supported lexers is available in the help.  If no
lexer is specified the library attempts to determine which lexer to use
automatically based on the filename.
"""

# ===========================================================================

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    common_arg(parser)
    filename_arg(parser)

    args = parser.parse_args()

    code = Code(args.filename, parser=args.parser)

    screen = SimpleScreen()
    box = screen.box

    if args.num:
        box.listing.starting_line_number = args.num


    box.actions.append(code)

    if args.highlight:
        parts = args.highlight.split(",")
        box.actions.highlight(*parts)

    screen.run()
