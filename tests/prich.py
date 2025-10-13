#! /usr/bin/env python
# tests/prich.py
#
# Prints a file containing a rich string
import argparse

from pathlib import Path

from rich.console import Console

# =============================================================================

parser = argparse.ArgumentParser(description=("Prints a file containing rich "
    "markup text"))
parser.add_argument("filename")
args = parser.parse_args()

console = Console(highlight=False)
console.rule()

path = Path(args.filename)
text = path.read_text()
console.print(text)

console.rule()
