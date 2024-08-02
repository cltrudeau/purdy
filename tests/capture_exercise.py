#!/usr/bin/env python
import os, sys, importlib, json
from pathlib import Path

# =============================================================================

def load_samples_module(mod_name):
    samples = Path(__file__).resolve()
    samples = samples.parent.parent / 'extras/samples'
    samples = samples.resolve()
    mod_name = mod_name.replace('.', '/')
    filename = samples / f'{mod_name}.py'

    # Change to samples dir, most of the scripts have local referenced files,
    # then save so we can reset afterwards
    current_dir = os.getcwd()
    os.chdir(samples)

    # Load the file as if it were a module
    spec = importlib.util.spec_from_file_location(mod_name, filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)

    os.chdir(current_dir)

    return module


def run_exercise(module_name):
    from purdy.settings import settings
    settings['deactivate_args'] = True

    module = load_samples_module(module_name)

    # Set up to use the ExerciseScreen implementation
    from purdy.ui import Factory
    Factory.name = 'exercise'

    if Factory.iscreen:
        # This has been called before in the same session (Factory is a
        # singleton), clear out the flipbook so it is empty
        Factory.iscreen.flipbook.pages = []

    module.screen.run(module.actions)

    return module.screen.iscreen.flipbook.pages


def capture(module_name):
    pages = run_exercise(module_name)

    with open('flipbook.json', 'w') as f:
        json.dump(pages, f, indent=2)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=('Captures the Cells used in '
        'the named sample program. Uses the ExerciseScreen mechanism that '
        'captures each change in a series of flip book pages. '
        'File must use global variables "screen" and "actions".'))

    parser.add_argument('module_name', help=('Name of module to load. Expects '
        'corresponding <module_name>.py file in the extras/samples directory'))

    args = parser.parse_args()
    capture(args.module_name)
