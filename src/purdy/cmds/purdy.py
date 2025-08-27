# purdy.py
import argparse

from argparse_formatter import FlexiFormatter

from purdy.content import Code
from purdy.cmds.arg_helpers import (filename_arg, general_args, motif_args,
    motif_factory)
from purdy.tui.apps import SimpleApp

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

general_args(parser)
motif_args(parser)
filename_arg(parser)

def main():
    args = parser.parse_args()
    code = Code(args.filename, args.lexer)
    motif = motif_factory(code, args)

    app = SimpleApp(motif)
    app.run()
