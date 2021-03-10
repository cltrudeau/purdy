#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates inserting lines of code with and without typewriter animation
from purdy.builder import ActionsBuilder
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=10)
code_box = screen.code_box
code_file = "../display_code/code.py"

for_loop = """\
        for x in range(1, 3):
           print(x)"""

two_lists = """\
        l1 = [5, 6, 7, 8, 9, ]
        l2 = [3, 1, 4, 5, ]"""

stuff = "        self.stuff(1)"

actions = (
    ActionsBuilder(screen, "py3")
    .append(code_file)
    .wait()
    .insert(8, text=for_loop)
    .wait()
    .insert_typewriter(8, text=two_lists)
    .insert(8, text=stuff)
)

if __name__ == "__main__":
    screen.run(actions)
