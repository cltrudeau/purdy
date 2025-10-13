#! /usr/bin/env python
# tests/print_compare.py
#
# Prints result from the "generate" functions to screen
import argparse

from pathlib import Path

import shared

# =============================================================================

def print_generated(name):
    base_dir = Path(__file__).parent / Path("compare")
    base_dir.mkdir(exist_ok=True)

    fn = getattr(shared, f"generate_{name}")
    text = fn()
    print(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("names")
    args = parser.parse_args()

    print_generated(args.names)
