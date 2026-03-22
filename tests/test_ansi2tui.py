from unittest import TestCase

from purdy.cmds.ansi2tui import parse_ansi

# ===========================================================================
# Result Constants
# ===========================================================================

ANSI_TEXT = """\033[0m'00'\033[0m
\033[0;35;1m>>> \033[0;32mf"\033[0m{\033[0;36mint\033[0m(\033[0;33m55.3\033[0m):\033[0;32m02x\033[0m}\033[0;32m"\033[0m\033[0m
'37'\033[0m"""

TEXTUAL_RESULT = """'00'
[magenta bold ]>>> [/][green]f"[/]{[cyan]int[/]([yellow]55.3[/]):[green]02x[/]}[green]"[/]
'37'"""

# =============================================================================

class AnsiTest(TestCase):
    def test_parse_ansi(self):
        result = parse_ansi(ANSI_TEXT)
        self.assertEqual(TEXTUAL_RESULT, result)
