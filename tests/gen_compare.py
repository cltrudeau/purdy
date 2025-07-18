#! /usr/bin/env python
# tests/gen_compare.py
#
# Creates files that are used to test the renderers.
import argparse

from pathlib import Path

import shared

# =============================================================================

def create_comparison_files(names):
    base_dir = Path(__file__).parent / Path("compare")
    base_dir.mkdir(exist_ok=True)

    for name in names:
        path = (base_dir / Path(f"{name}.out")).resolve()
        print(path)
        fn = getattr(shared, f"generate_{name}")
        text = fn()
        path.write_text(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="*", default=shared.RENDER_TESTS)
    args = parser.parse_args()

    create_comparison_files(args.names)
