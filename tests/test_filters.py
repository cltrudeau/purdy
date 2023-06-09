from unittest import TestCase

from purdy.filters import (python_extractor, remove_lines, remove_double_blanks,
    left_justify)

# =============================================================================

class FiltersTest(TestCase):
    def test_python_extractor(self):
        cat = (
            "class Cat:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n\n"
        )

        cat_method = (
            "    def meow(self):\n"
            "        print(f'Meow, {name}')\n"
        )

        dog = (
            "def dog(woof):\n"
            "    print('Woof, woof')\n"
            "    print(woof)\n"
        )

        snake = (
            "def snake(slither):\n"
            "    slither = slither + 5\n"
            "    return slither\n"
        )

        turtle = "turtle = True\n"

        source = cat + cat_method + "\n\n" + dog + "\n\n" + snake + "\n\n" \
            + turtle

        # Extract the Cat class
        filtrate = python_extractor("Cat")
        result = filtrate.filter(source)
        self.assertEqual(cat + cat_method, result)

        # Extract the meow class
        filtrate = python_extractor("Cat.meow")
        result = filtrate.filter(source)
        self.assertEqual(cat_method, result)

        # Extract the dog function
        filtrate = python_extractor("dog")
        result = filtrate.filter(source)
        self.assertEqual(dog, result)

        # Extract the turtle value
        filtrate = python_extractor("turtle")
        result = filtrate.filter(source)
        self.assertEqual(turtle, result)

        # Test bad name
        filtrate = python_extractor("dragon")
        result = filtrate.filter(source)
        self.assertEqual('', result)

    def test_remove_lines(self):
        source = (
            "She walks in beauty\n"
            "like the night,\n"
            "Of cloudless climes\n"
            "and starry skies;\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;\n"
        )

        # Remove two single lines
        expected = (
            "like the night,\n"
            "and starry skies;\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;\n"
        )

        filtrate = remove_lines(1, 3)
        result = filtrate.filter(source)
        self.assertEqual(expected, result)

        # Remove with tuples
        expected = (
            "like the night,\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;\n"
        )
        filtrate = remove_lines(1, (3, 2))
        result = filtrate.filter(source)
        self.assertEqual(expected, result)

    def test_remove_double_blanks(self):
        filtrate = remove_double_blanks()

        # Source doesn't end in newline
        source = (
            "She walks in beauty\n"
            "like the night,\n\n"
            "Of cloudless climes\n\n"
            "and starry skies;\n\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;"
        )

        expected = (
            "She walks in beauty\n"
            "like the night,\n"
            "Of cloudless climes\n"
            "and starry skies;\n"
            "And all that's best of dark and bright\n"
            "Meet in her aspect and her eyes;"
        )

        result = filtrate.filter(source)
        self.assertEqual(expected, result)

        # Source ends in single newline
        source += "\n"
        expected += "\n"
        result = filtrate.filter(source)
        self.assertEqual(expected, result)

        # Source ends in double newline
        source += "\n"
        result = filtrate.filter(source)
        self.assertEqual(expected, result)

    def test_left_justify(self):
        # Nothing to justify
        source = (
            "One two three\n"
            "four five six\n"
            "seven eight nine\n"
        )

        filtrate = left_justify()
        result = filtrate.filter(source)
        self.assertEqual(source, result)

        # Mixed indent
        source = (
            "    One two three\n"
            "        four five six\n"
            "    seven eight nine\n"
        )

        expected = (
            "One two three\n"
            "    four five six\n"
            "seven eight nine\n"
        )

        result = filtrate.filter(source)
        self.assertEqual(expected, result)

    def test_left_justify_bad(self):
        source = "   \n\n\n"
        filtrate = left_justify()
        result = filtrate.filter(source)
        self.assertEqual(source, result)
