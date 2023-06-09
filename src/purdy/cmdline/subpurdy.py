# subpurdy.py
#
# Meta-command for running various purdy operations

import argparse

from purdy.cmdline.utils import common_arg, filename_arg, process_args
from purdy.content import Code, Listing

# ===========================================================================

DESCRIPTION = """This colourizes and outputs a program file using a variety of
output types. Subcommand indicate what kind of output, while colourization is
based on a named parser."""

# ===========================================================================
# Commands
# ===========================================================================

def print_tokens(listing, args):
    if args.blackandwhite:
        from purdy.export.text import listing_to_tokens_outline
        print(listing_to_tokens_outline(listing))
    else:
        from purdy.export.ansi import listing_to_tokens_ansi
        print(listing_to_tokens_ansi(listing))


def print_ansi(listing, args):
    from purdy.export.ansi import listing_to_ansi
    print(listing_to_ansi(listing))


def print_html(listing, args):
    from purdy.export.html import listing_to_html
    print(listing_to_html(listing, args.snippet))


def print_rtf(listing, args):
    from purdy.export.rtf import listing_to_rtf
    print(listing_to_rtf(listing, args.background))

# ===========================================================================

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    common_arg(parser)

    subparsers = parser.add_subparsers(title='commands', dest='command')
    subparsers.required = True

    # --- Token sub-command
    sub = subparsers.add_parser('tokens', help=('Parses the given file and '
        'prints the tokenized output to the screen'))
    sub.set_defaults(func=print_tokens)
    sub.add_argument('--blackandwhite', '--bw', action='store_true',
        help=("By default this command uses colourized terminal codes. Using "
        "this flag causes the output to be plain text"))

    # --- ANSI sub-command
    sub = subparsers.add_parser('ansi', help=('Parses the given file and '
        'prints colourized version to the screen'))
    sub.set_defaults(func=print_ansi)

    # --- HTML sub-command
    sub = subparsers.add_parser('html', help=('Parses the given file and '
        'prints an HTML version to the screen'))
    sub.add_argument('--snippet', action='store_true', help=("By default this "
        "command displays an entire HTML document, with this flag enabled "
        "only the inner display <div> is output"))
    sub.set_defaults(func=print_html)

    # --- RTF sub-command
    sub = subparsers.add_parser('rtf', help=('Parses the given file and '
        'prints an RTF version to the screen'))
    sub.add_argument('--background', default=None, help=("Change the "
        "background colour. Defaults to white"))
    sub.set_defaults(func=print_rtf)

    ######
    # Add the filename argument after the subparser
    filename_arg(parser)

    args = parser.parse_args()
    code = Code(args.filename, parser=args.parser)
    listing = Listing(code)

    process_args(listing, args)

    # Call the sub-command
    args.func(listing, args)
