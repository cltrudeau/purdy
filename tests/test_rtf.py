from unittest import TestCase

from pygments.token import Comment, Keyword, Name

from purdy.content import Code, MultiCode
from purdy.renderers.rtf import RTFDoc, RTFFormatter
from purdy.themes import Theme

# =============================================================================

class TestRTF(TestCase):
    def test_rtf_colour(self):
        theme = Theme("dummy_theme", {
            Comment: "112233",
            Keyword: ("223344", "556677", "bold"),
            Name: "abc",
        })

        code = Code.text("", "plain")
        code.theme = theme
        mc = MultiCode(code)

        doc = RTFDoc("222222", mc)

        # Test map (0 is the auto value, starts at 1)
        expected = {
            "222222": (1, r"\red34\green34\blue34"),
            "112233": (2, r"\red17\green34\blue51"),
            "223344": (3, r"\red34\green51\blue68"),
            "556677": (4, r"\red85\green102\blue119"),
            "abc": (5, r"\red170\green187\blue204"),
        }
        self.assertEqual(expected, doc.colour_table)

        # Test table
        expected = (
            r"{\colortbl;"
            r"\red34\green34\blue34;"
            r"\red17\green34\blue51;"
            r"\red34\green51\blue68;"
            r"\red85\green102\blue119;"
            r"\red170\green187\blue204;"
            r"}"
        )
        self.assertIn(expected, doc.header_string)

    def test_encode(self):
        # ASCII text
        self.assertEqual("a", RTFFormatter.rtf_encode("a"))
        self.assertEqual(r"a\\b", RTFFormatter.rtf_encode(r"a\b"))

        # ASCII above 127
        c = chr(200)  # hex C8
        self.assertEqual(r"\'c8", RTFFormatter.rtf_encode(c))

        # Unicode above 256 but below word boundary
        c = chr(257)
        self.assertEqual(r"\uc0\u257", RTFFormatter.rtf_encode(c))

        # Unicode above 0xD800 is two words
        c = "😂"
        self.assertEqual(r"\uc0\u55357 \u56834", RTFFormatter.rtf_encode(c))
