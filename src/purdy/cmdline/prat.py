# prat.py
#
# Purdy based RTF output

import argparse

from purdy.cmdline.utils import common_arg, filename_arg, process_args
from purdy.content import Code, Listing
from purdy.export.rtf import listing_to_rtf

# ===========================================================================

DESCRIPTION = """This command prints colourized RTF version of a file,
parsing the file based on a limited number of pygments lexers. 'prat' is part
of the 'purdy' library. A list of supported lexers is available in the help.
If no lexer is specified the library attempts to determine which lexer to user
automatically.
"""

# ===========================================================================

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    common_arg(parser)
    filename_arg(parser)

    parser.add_argument('--background', default=None, help=("Change the "
        "background colour. Defaults to white"))

    args = parser.parse_args()

    code = Code(args.filename, parser=args.parser)
    listing = Listing(code)

    process_args(listing, args)

    print(listing_to_rtf(listing, args.background))
