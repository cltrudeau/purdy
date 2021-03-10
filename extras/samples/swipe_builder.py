#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the slide transition animation
from purdy.builder import ActionsBuilder
from purdy.actions import Append, Fold
from purdy.content import Code
from purdy.ui import SimpleScreen, VirtualCodeBox

screen = SimpleScreen(starting_line_number=10)
code_box = screen.code_box
blob = "../display_code/simple.repl"
blob2 = "../display_code/traceback.repl"
blob3 = Code("../display_code/decorator.repl")

vbox = VirtualCodeBox(starting_line_number=20, display_mode="urwid")

# prep vbox for copy
vbox.perform_actions(
    [
        Append(vbox, blob3),
        Fold(vbox, 2, 2),
    ]
)

actions = (
    ActionsBuilder(screen, "con")
    .append(filename=blob2)
    .wait()
    .transition()  # test transition to empty
    .append(filename=blob)
    .wait()
    .transition(code_box_to_copy=vbox)  # Test Wait after Transition and code box copy
    .wait()
    .append(filename=blob2)
)

# actions = [
#     Append(code_box, blob2),
#     Wait(),
#     Transition(code_box),  # test transition to empty
#     Append(code_box, blob),
#     Wait(),
#     # Test Wait after Transition and code box copy
#     Transition(code_box, code_box_to_copy=vbox),
#     Wait(),
#     Append(code_box, blob2),
# ]

if __name__ == "__main__":
    screen.run(actions)
