from tests.base import PurdyCase

from purdy.content import Code, Listing
from purdy.tui.screen import CodeBox, _BaseScreen
from purdy.tui.animation import animator

# =============================================================================

class ActionTest(PurdyCase):
    def test_simple_append(self):
        # Creates an animation with two steps and a wait in between
        first = "She walks in beauty"
        second = "like the night."

        box = CodeBox()
        screen = _BaseScreen([box])

        (box.actions
            .append(first)
            .wait()
            .append(second)
        )

        # Cause the first animation
        animator.forward()

        self.assertEqual(1, len(box.listing.lines))
        self.assertEqual(first, box.listing.lines[0].parts[0].text)

        # Cause the second animation
        animator.forward()

        self.assertEqual(2, len(box.listing.lines))
        self.assertEqual(first, box.listing.lines[0].parts[0].text)
        self.assertEqual(second, box.listing.lines[1].parts[0].text)

        # Try an undo
        animator.backward()

        self.assertEqual(1, len(box.listing.lines))
        self.assertEqual(first, box.listing.lines[0].parts[0].text)

        # Undo again should empty it out
        animator.backward()
        self.assertEqual(0, len(box.listing.lines))

        # Undo again should do nothing
        animator.backward()
        self.assertEqual(0, len(box.listing.lines))
