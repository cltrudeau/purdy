"""
Command Line Tools
==================

Several of the command line tools have common arguments and needs. This file 
defines helper functions so these are defined once.
"""
from purdy.__init__ import __version__
from purdy.parser import PurdyLexer

LEXER_HELP = ('Name of lexer to use to parse the file. Choices are: ' 
    f'{PurdyLexer.choices()}. If no choice given, attempts to determine the '
    'result automatically. If it cannot detect it, it assumes Python 3.')

# =============================================================================
# Argument Builders for argparse
# =============================================================================

def max_height_arg(parser):
    parser.add_argument('--maxheight', help=('Sets a maximum screen height '
        'for the TUI screen viewer. Ignored if not in TUI mode.'), type=int, 
        default=0)

def num_arg(parser):
    parser.add_argument('--num', help=('Display line numbers with code '
        'starting with the value given here'), type=int, default=-1)


def lexer_arg(parser):
    parser.add_argument('-l', '--lexer', choices=PurdyLexer.names(),
        default='detect', help=LEXER_HELP)


def version_arg(parser):
    parser.add_argument('--version', action='version', 
        version='%(prog)s {version}'.format(version=__version__ ))


def filename_arg(parser):
    parser.add_argument('filename', help='Name of file to parse')


def highlight_arg(parser):
    parser.add_argument('--highlight', '--hl', help=('Highlight certain line '
        'numbers when displaying the code. Line numbers are 1-indexed. '
        'Multiple lines can be higlighted using a hyphen for range (e.g. 1-4, '
        'inclusive) or a comma separated list (e.g. 1-4,7,9 is line 1, 2, 3, '
        '4, 7 and 9).'))


def background_arg(parser):
    parser.add_argument('--background', '--bg', help=('Change the background '
        'colour of the document. When using the --highlight option, you '
        'you should also set a background colour, otherwise the background '
        'will turn white due to how RTF supports colouring. Format of the '
        'colour is like an HTML colour, e.g. #c1b455, without the leading '
        '#'))

# =============================================================================
# Meta Argument Builders
# =============================================================================

def general_args(parser):
    lexer_arg(parser)
    version_arg(parser)


def rtf_args(parser):
    num_arg(parser)
    background_arg(parser)
    highlight_arg(parser)


def ansi_args(parser):
    num_arg(parser)
    highlight_arg(parser)
