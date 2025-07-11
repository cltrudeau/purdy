from unittest import TestCase

from purdy.content.plain import TextCode

# =============================================================================

class TestCodeHandlers(TestCase):
    def print_lines(self, code):
        # Prints output from the plain.TextCode
        print("****")
        for line in code:
            if line is None:
                print(line)
            else:
                print(line, end='')
        print("****")

    def test_access(self):
        # Sample text numbers 1-10 separated by newlines
        text = "\n".join([str(x) for x in range(1, 11)]) + "\n"
        code = TextCode(text, "plain")

        self.assertEqual("1\n", code[0])
        self.assertEqual("10\n", code[-1])

    def test_folding(self):
        # Sample text numbers 1-10 separated by newlines
        text = "\n".join([str(x) for x in range(1, 11)]) + "\n"
        code = TextCode(text, "plain")

        # Fold lines 2 through 9
        code.fold(1, 8)

        self.assertEqual("1\n", code[0])
        self.assertEqual("⠇\n", code[1])
        self.assertIsNone(code[2])
        self.assertIsNone(code[8])
        self.assertEqual("10\n", code[-1])

        # Unfold
        code.unfold(1)
        self.assertEqual("2\n", code[1])
        self.assertEqual("3\n", code[2])

        # Multiple folds
        code.fold(1, 1)
        code.fold(5, 2)
        self.assertEqual("1\n", code[0])
        self.assertEqual("⠇\n", code[1])
        self.assertEqual("3\n", code[2])
        self.assertEqual("⠇\n", code[5])
        self.assertIsNone(code[6])
        self.assertEqual("8\n", code[7])
        self.assertEqual("10\n", code[-1])
