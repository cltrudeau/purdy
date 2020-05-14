import json
from pathlib import Path
from unittest import TestCase

from tests.capture_sample import load_samples_module

# =============================================================================

class TestSamples(TestCase):
    def test_samples(self):
        self.maxDiff = None
        samples = ['all_console', 'append', 'bash_console', 'cols', 
            'docstring', 'exec', 'highlight', 'insert', 'lines', 'mixed', 
            'mls_type', 'movie_console', 'remove', 'replace', 'split_long', 
            'swipe', 'tall', 'triple', 'type_console', ]

        sample_data = Path(__file__).parent / 'samples_data'

        for sample in samples:
            # load stored expected results
            filename = sample_data / f'{sample}.json'
            with open(filename) as f:
                expected = json.load(f)

            # load the module and turn the actions in to _test_dict's
            module = load_samples_module(sample)
            module.screen.load_actions(module.actions)

            results = []
            for cell in module.screen.base_window.animation_manager.cells:
                results.append( cell._test_dict() )

            with open('last_output.json', 'w') as f:
                json.dump(results, f, indent=2)

            self.assertEqual(expected, results, 
                msg=f'Compare failed for {sample}' )
