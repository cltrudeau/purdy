from pathlib import Path
from unittest import TestCase

from purdy.content import Code

# =============================================================================

class TestCode(TestCase):
    def test_code(self):
        text = "\n".join([str(x) for x in range(0, 10)]) + "\n"

        # Constructor as factory
        path = (Path(__file__).parent / Path("data/count.txt")).resolve()
        code = Code(path, "plain")

        self.assertEqual(10, len(code))
        self.assertEqual("0", code[0].parts[0].text)
        self.assertEqual("9", code[9].parts[0].text)

        # Text based factory
        code = Code.text(text, "plain")

        self.assertEqual(10, len(code))
        self.assertEqual("0", code[0].parts[0].text)
        self.assertEqual("9", code[9].parts[0].text)

        # Spawn
        spawn = code.spawn()
        self.assertEqual(code.parser, spawn.parser)
        self.assertEqual(0, len(spawn))
