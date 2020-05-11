#!/usr/bin/env python
import os, sys, importlib, json
from pathlib import Path

# =============================================================================

def load_samples_module(mod_name):
    samples = Path(__file__).resolve()
    samples = samples.parent.parent / 'extras/samples'
    samples = samples.resolve()
    filename = samples / f'{mod_name}.py'

    # Change to samples dir, most of the scripts have local referenced files, 
    # then wipe out 
    current_dir = os.getcwd()
    os.chdir(samples)

    # Load the file as if it were a module
    spec = importlib.util.spec_from_file_location(mod_name, filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)

    os.chdir(current_dir)

    return module


def capture(module_name):
    module = load_samples_module(module_name)

    module.screen.load_actions(module.actions)

    results = []
    for cell in module.screen.base_window.animation_manager.cells:
        results.append( cell._test_dict() )

    with open('cells.json', 'w') as f:
        json.dump(results, f, indent=2)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=('Captures the Cells used in '
        'the named sample program. Utility for creating Cell repr files to be '
        'used in testing. File must global variables "screen" and "actions".'))

    parser.add_argument('module_name', help=('Name of module to load. Expects '
        'corresponding <module_name>.py file in the extras/samples directory'))

    args = parser.parse_args()
    capture(args.module_name)
