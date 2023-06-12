from tests.base import PurdyCase

from purdy.tui.screen import CodeBox, _BaseScreen
from purdy.content import Code, Listing

# =============================================================================

class ActionTest(PurdyCase):
    def test_simple_append(self):
        # Creates an animation that has an initial state, appends, waits, then
        # appends some more
        first = "She walks in beauty"
        second = "like the night,"
        third = "Of cloudless climes"

        code = Code(text=first, parser='plain')
        listing = Listing(code)
        box = CodeBox(listing)

        screen = _BaseScreen([box])
        box = screen.boxes["box0"]

        (screen.actions
            .append(box, second)
            .wait()
            .append(box, third)
        )

        # Verify it as built correctly
        self.assertEqual(1, len(box.listing.lines))
        self.assertEqual(first, box.listing.lines[0].parts[0].text)

        # Cause the first animation
        screen.actions._forwards()

        self.assertEqual(2, len(box.listing.lines))
        self.assertEqual(first, box.listing.lines[0].parts[0].text)
        self.assertEqual(second, box.listing.lines[1].parts[0].text)

        # Cause the second animation
        screen.actions._forwards()

        self.assertEqual(3, len(box.listing.lines))
        self.assertEqual(first, box.listing.lines[0].parts[0].text)
        self.assertEqual(second, box.listing.lines[1].parts[0].text)
        self.assertEqual(third, box.listing.lines[2].parts[0].text)

        # Try an undo
        screen.actions._backwards()
        self.assertEqual(2, len(box.listing.lines))
        self.assertEqual(first, box.listing.lines[0].parts[0].text)
        self.assertEqual(second, box.listing.lines[1].parts[0].text)

        # Undo again
        screen.actions._backwards()
        self.assertEqual(1, len(box.listing.lines))
        self.assertEqual(first, box.listing.lines[0].parts[0].text)

        # Undo again should do nothing
        screen.actions._backwards()
        self.assertEqual(1, len(box.listing.lines))
        self.assertEqual(first, box.listing.lines[0].parts[0].text)
