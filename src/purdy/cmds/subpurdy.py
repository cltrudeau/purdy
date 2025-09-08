# subpurdy.py
import argparse

from argparse_formatter import FlexiFormatter
from rich.console import Console

from purdy.cmds.arg_helpers import (filename_arg, general_args, no_colour_arg,
    mc_args, multicode_factory)
from purdy.renderers.html import to_html
from purdy.renderers.rich import to_rich
from purdy.renderers.rtf import to_rtf
from purdy.scribe import print_code_lines

# =============================================================================

DESCRIPTION = """Purdy is a library and set of command line tools for
displaying code. You can use the library to write your display animations, or
use the subcommands of this program for preset usages. The 'purdy' command
uses the Textual library to display a colourized version of your code in the
console, while 'subpurdy' command is a set of utilities for printing different
styles of code to the screen.
"""

console = Console(highlight=False)
rprint = console.print

# =============================================================================
# Subcommands
# =============================================================================

def tokens(args):
    ### 'tokens' sub-command: prints lines and tokens to screen
    mc = multicode_factory(args)
    print_code_lines(mc[0].lines, title_enabled=False, no_colour=args.nocolour)


def ansi(args):
    ### 'ansi' sub-command: prints content with ANSI colour highlighting
#    mc = multicode_factory(args)
    mc = multicode_factory(args, theme_name="pyrepl")
    output = to_rich(mc)
    rprint(output)


def html(args):
    ### 'html' sub-command: prints content as an HTML div
    mc = multicode_factory(args)
    output = to_html(mc, not args.fullhtml)
    print(output)


def rtf(args):
    ### 'rtf' sub-command: prints content in RTF format
    mc = multicode_factory(args, "rtf")
    output = to_rtf(mc)
    print(output)

# =============================================================================
# Main
# =============================================================================

parser = argparse.ArgumentParser(description=DESCRIPTION,
    formatter_class=FlexiFormatter)

# === Common flags ===
general_args(parser)

# === Subcommands ===
subparsers = parser.add_subparsers(title="subcommands", dest="command")
subparsers.required = True

# --- tokens cmd
sub = subparsers.add_parser("tokens", help=("Prints out each line in a file "
    "with the corresponding tokens indented beneath it"))
no_colour_arg(sub)
sub.set_defaults(func=tokens)

# --- ansi cmd
sub = subparsers.add_parser("ansi", help=("Prints code with colourized ANSI "
    "results in your terminal"))
mc_args(sub)
sub.set_defaults(func=ansi)

# --- html cmd
sub = subparsers.add_parser("html", help="Prints code as HTML")
sub.add_argument("--fullhtml", help=("By default only a div with the code is "
    "shown. This flag causes a full HTML doc."), action="store_true")
mc_args(sub)
sub.set_defaults(func=html)

# --- rtf cmd
sub = subparsers.add_parser("rtf", help="Prints code as RTF")
mc_args(sub)
sub.set_defaults(func=rtf)

# === Positional filename argument common to all subs
filename_arg(parser)

def main():
    args = parser.parse_args()
    args.func(args)
