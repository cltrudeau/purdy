from unittest import TestCase

from waelstow import capture_stdout

from purdy.scribe import range_set_to_list

# =============================================================================

class TestUtils(TestCase):
    def test_range_set_to_list(self):
        expected = [3,]
        result = range_set_to_list('3')
        self.assertEqual(expected, result)

        expected = [3, 4, 5]
        result = range_set_to_list('3-5')
        self.assertEqual(expected, result)

        expected = [3, 4, 5, 6, 7, 8, 9]
        result = range_set_to_list('3-5,9,4,5-8')
        self.assertEqual(expected, result)
