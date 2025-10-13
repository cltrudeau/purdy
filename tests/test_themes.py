from unittest import TestCase

from pygments.token import Keyword, Comment

from purdy.themes import Theme

# =============================================================================

class TestThemes(TestCase):
    def test_themes(self):

        # Theme inheritance
        theme = Theme("first", {Comment: "778899"})
        second = Theme("second", {Keyword: "889900"}, theme)

        self.assertEqual(2, len(second.colour_map))
        self.assertIn(Comment, second.colour_map)
        self.assertIn(Keyword, second.colour_map)

        # Values iterator
        theme = Theme("third", {
            Comment: "112233",
            Keyword: ("223344", "556677", "bold"),
        })

        expected = [
            (Comment, "112233", "", ""),
            (Keyword, "223344", "556677", "bold"),
        ]
        result = list(theme.values())
        self.assertEqual(expected, result)
