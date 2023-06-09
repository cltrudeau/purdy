# pat.py
#
# Command for displaying a file to the screen using ANSI colourization

import argparse

from purdy.cmdline.utils import common_arg, filename_arg
from purdy.content import Code, Listing
from purdy.export.ansi import listing_to_ansi

# ===========================================================================

DESCRIPTION = """This command prints ANSI colourized versions of a file,
parsing the file based on a limited number of pygments lexers. 'pat' is part
of the 'purdy' library. A list of supported lexers is available in the help.
If no lexer is specified the library attempts to determine which lexer to use
automatically based on the filename.
"""

# ===========================================================================

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    common_arg(parser)
    filename_arg(parser)

    args = parser.parse_args()

    code = Code(args.filename, parser=args.parser)
    listing = Listing(code)

    if args.num:
        listing.starting_line_number = args.num

    if args.highlight:
        parts = args.highlight.split(",")
        listing.highlight(*parts)

    result = listing_to_ansi(listing)
    print(result)
