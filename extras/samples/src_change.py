#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the use of methods on Code to modify source before display

from purdy.actions import Append, Transition, Wait
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen(starting_line_number=1)
box = screen.code_box

SOURCE = """\
    # Before
    def show_only_this_function():
        # This comment is deleted
        # As is this one
        

        # Above should be a single blank
        print()

        # This comment should be replaced
        # Replace between the dollar signs $replace me$

        # Fold the numbers in the following
        # a
        # 1
        # 2
        # b
        return


    def should_be_culled():
        pass
"""

before = Code(text=SOURCE)
after = Code(text=SOURCE).left_justify()
after.python_portion('show_only_this_function')
after.insert_line(1, "# After")
after.remove_lines(3, 2)
after.replace_line(8, '    # Was replaced')
after.inline_replace(9, 41, 'done$')
after.fold_lines(13, 14)
after.remove_double_blanks()

actions = [
    Append(box, before),
    Wait(),
    Transition(box, after),
]

if __name__ == '__main__':
    screen.run(actions)
