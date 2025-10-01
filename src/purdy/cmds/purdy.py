# purdy.py
import argparse

from argparse_formatter import FlexiFormatter

from purdy.cmds.arg_helpers import purdy_client_args
from purdy.tui import AppFactory, Code

# =============================================================================

DESCRIPTION = """Purdy is a library and set of command line tools for
displaying code. You can use the library to write your display animations, or
use this program as a code viewer.
"""

# =============================================================================
# Main
# =============================================================================

parser = argparse.ArgumentParser(description=DESCRIPTION,
    formatter_class=FlexiFormatter)

purdy_client_args(parser)

def main():
    args = parser.parse_args()

    theme_name = args.theme
    if args.nocolour:
        if args.theme != "detect":
            parser.exit("Cannot specify both 'nocolur' and 'theme'")

        # Override theme
        theme_name = "no_colour"

    code = Code(args.filename, args.lexer, theme_name)

    app = AppFactory.simple(args.maxheight)
    doc = app.box.doc

    if hasattr(args, "num") and args.num:
        doc.line_numbers_enabled = True
        doc.starting_line_number = args.num

    if hasattr(args, "wrap") and args.wrap:
        doc.wrap = args.wrap

    if hasattr(args, "highlight") and args.highlight:
        code.highlight(*args.highlight)

    if args.notyping:
        app.box.append(code)
    else:
        app.box.typewriter(code)

    app.run()
