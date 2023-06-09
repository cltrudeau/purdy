from unittest import TestCase

from purdy.export.ansi import listing_to_tokens_ansi

# =============================================================================

class PurdyCase(TestCase):
    def print_tokens(self, listing):
        print(listing_to_tokens_ansi(listing))
