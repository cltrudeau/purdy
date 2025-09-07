# arg_helpers.py
#
# Helper utilities for the command line arguments used by 'purdy' and
# 'subpurdy'
from purdy.__init__ import __version__
from purdy.content import Code, MultiCode
from purdy.parser import LexerSpec

# =============================================================================
# Motif Factory
# =============================================================================

def multicode_factory(args, theme_name="default"):
    if args.nocolour:
        # Override theme
        theme_name = "no_colour"

    code = Code(args.filename, args.lexer, theme_name)
    mc = MultiCode(code)

    # Arguments are conditional on the subcommand, so not all args are
    # available all the time
    if hasattr(args, "bg"):
        mc.background = args.bg

    if hasattr(args, "num") and args.num:
        mc.line_numbers_enabled = True
        mc.starting_line_number = args.num

    if hasattr(args, "wrap") and args.wrap:
        mc.wrap = args.wrap

    if hasattr(args, "highlight") and args.highlight:
        code.highlight(*args.highlight)

    return mc

# =============================================================================
# Argument Builders for argparse
# =============================================================================

def lexer_arg(parser):
    lexer_help = (
        "Name of lexer to use to parse the file. Defaults to automaticallly "
        "detecting based on name of file. Choices are:\n"
    )

    for key, value in LexerSpec.built_ins.items():
        lexer_help += f"   * '{key}' -- {value.description}\n"

    for key, value in LexerSpec.aliases.items():
        lexer_help += f"   * '{key}' -- Alias for {value}\n"

    parser.add_argument("-l", "--lexer", choices=LexerSpec.names,
        default="detect", help=lexer_help)


def version_arg(parser):
    parser.add_argument("--version", action="version",
        version="%(prog)s {version}".format(version=__version__ ))


def filename_arg(parser):
    parser.add_argument("filename", help="Name of file to parse")

# -----------------------------------------------------------------------------

def num_arg(parser):
    parser.add_argument("--num", help=("Display line numbers with code "
        "starting with the value given here"), type=int, default=None)


def wrap_arg(parser):
    parser.add_argument("--wrap", help="Wrap line width at this value",
        type=int, default=None)


def no_colour_arg(parser):
    parser.add_argument("--nocolour", "--nc", help=("By default code is "
        "colourized. This flag turns that off."),
        action="store_true")


def highlight_arg(parser):
    parser.add_argument("--highlight", "--hl",
        help=(
            "Highlight a code segment. This argument can be used multiple"
            "times. Each value can be a line number (zero-indexed, negative "
            "indexing supported, a range separated by a dash ('1-3' index 1, "
            "2, and 3 highlighted), or highlight within the line ('3:10,5' "
            "for index 3, highlighting starting at character 10, for 5 "
            "characters"
        ), action="append")


def bg_arg(parser):
    parser.add_argument("--bg", help=(
            "Change the background colour. Indicated using hex RRGGBB format, "
            "like HTML #AABBCC, but without the leading #"
        ), type=str, default=None)

# =============================================================================
# Grouped Argument Builders
# =============================================================================

def general_args(parser):
    lexer_arg(parser)
    version_arg(parser)


def mc_args(parser):
    num_arg(parser)
    wrap_arg(parser)
    no_colour_arg(parser)
    highlight_arg(parser)
    bg_arg(parser)
