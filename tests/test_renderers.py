from pathlib import Path
from unittest import TestCase

import shared

# =============================================================================

class TestRenderers(TestCase):
    def test_renderers(self):
        compare_dir = Path(__file__).parent / Path("compare")

        for name in shared.RENDER_TESTS:
            # Read the comparison file
            path = (compare_dir / Path(f"{name}.out")).resolve()
            expected = path.read_text()

            # Generate the output to compare against
            fn = getattr(shared, f"generate_{name}")
            text = fn()

            try:
                # Convert to list as it makes finding the problem easier
                nexpected = expected.split("\n")
                ntext = text.split("\n")
                self.assertEqual(nexpected, ntext)
            except AssertionError: # pragma: no cover
                print(f"*** Failed when testing {name}")
                raise
