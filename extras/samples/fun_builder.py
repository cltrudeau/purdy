#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the RunFunction action
from builder import ActionsBuilder
from purdy.ui import SimpleScreen


def do_something(foo, bar=3):
    with open("zzz_output.txt", "a") as f:
        f.write(f"Doing something {foo} {bar}\n")


def undo_something(foo, bar=3):
    with open("zzz_output.txt", "a") as f:
        f.write(f"Undoing something {foo} {bar}\n")


screen = SimpleScreen(starting_line_number=10)
first = "First things first"
second = "Second things second"
third = "Now read zzz_output.txt file to check it worked"

actions = (
    ActionsBuilder(screen, "py3")
    .append(first)
    .wait()
    .run_function(do_something, undo_something, "FOO", bar=42)
    .wait()
    .append(second)
    .append(third)
)

if __name__ == "__main__":
    screen.run(actions)
