# ansi2tui.py
import argparse

from typing import Tuple

import pyperclip

from ansiscape import Sequence
from ansiscape.enums import MetaColor, NamedColor, Weight

# =============================================================================

SHORT_DESCRIPTION = """Reads ANSI colour sequences text from the clipboard and
outputs Textual TUI markup"""

DESCRIPTION = """This utility converts text containing ANSI colour sequences
(8-bit/256 colour or lower) to Textual TUI markup. It reads from the clipboard
and outputs the equivalent markup to the screen. If you are running the macOS
iTerm2 program, use 'Copy With Control Sequences' from the 'Edit' menu to copy
highlighted text from the terminal in a compatible fashion."""

# =============================================================================
# Main
# =============================================================================

parser = argparse.ArgumentParser(description=SHORT_DESCRIPTION,
    epilog=DESCRIPTION)


def convert_colour(colour):
    if isinstance(colour, Tuple):  # RGBA is an alias of Tuple
        raise ValueError("ansi2tui does not support 24-bit colour terminals")

    if isinstance(colour, NamedColor):
        return colour.name.lower()

    if colour == MetaColor.DEFAULT:
        return ""


def parse_ansi(content):
    seq = Sequence(content)
    output = ''
    open_tag = False

    for part in seq.resolved:
        if isinstance(part, str):
            output += part
        elif isinstance(part, dict):
            if part == {"background": MetaColor.DEFAULT}:
                # Reset if there is an open tag
                if open_tag:
                    output += "[/]"
                    open_tag = False
            else:
                if part.get("background") == MetaColor.DEFAULT and open_tag:
                    # Close anything that is open
                    output += "[/]"

                open_tag = True
                output += "["
                if colour := part.get("foreground"):
                    output += convert_colour(colour)

                if colour := part.get("background"):
                    # convert_colour ignores MetaColor.DEFAULT, so this
                    # repetition ok
                    response = convert_colour(colour)
                    if response:
                        output += " on " + response

                if weight := part.get("weight"):
                    if weight == Weight.HEAVY:
                        output += " bold "

                output += "]"

    return output


def main():
    # No real args for this program, argparse is there for the help command
    parser.parse_args()

    # Read input from the clipboard
    output = parse_ansi(pyperclip.paste())
    print(output)
