# utils.py
#
# Functions that group together argparse definitions

from purdy.__init__ import __version__
from purdy.parser import Parser

# ===========================================================================

PARSER_HELP = (
    'Name of parser to use to parse the file. Choices are: '
    f'{Parser.choices()}. If no choice given, attempts to determine the '
    'result based on the filename.'
)

HIGHLIGHT_HELP = (
    'Highlight sections of the output. Numbers are 1-indexed. Supports '
    'multiple lines being highlighted through a comma-separated list. '
    'Ranges can be specified using hyphens, and highlighting part of a '
    'line is supported using a decimal notation. For example "1,3-4,6.10-20" '
    'highlights lines 1, lines 3 through 4 (inclusive) and characters 10 '
    'through 20 (inclusive) on line 6'
)

# ===========================================================================
# ArgParse Argument Definition Functions
# ===========================================================================

def common_arg(parser):
    parser.add_argument("--highlight", "-l", help=HIGHLIGHT_HELP, default='')

    parser.add_argument("--num", "-n", action="store_true",
        help="Display line numbers")

    parser.add_argument("--startnum", type=int,
        help="Display line numbers starting with the value given")

    parser.add_argument('--parser', '-p', choices=Parser.names,
        default='detect', help=PARSER_HELP)

    parser.add_argument('--version', action='version',
        version='%(prog)s {version}'.format(version=__version__))


def filename_arg(parser):
    parser.add_argument('filename', help='Name of file to parse')

# ---------------------------------------------------------------------------

def process_args(listing, args):
    # Common handling of parsed args and their effect on the listing

    if args.num:
        listing.starting_line_number = 1
    elif args.startnum:
        listing.starting_line_number = args.startnum

    if args.highlight:
        parts = args.highlight.split(",")
        listing.highlight(*parts)
