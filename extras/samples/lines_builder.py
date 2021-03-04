#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates appending strings to the end of existing lines as well as
# replacing lines. Both done with and without the typewriter animation.
from builder import ActionsBuilder
from purdy.ui import SplitScreen

screen = SplitScreen(top_starting_line_number=10)

function = """\
@decorator
def foo(x):
    \"\"\"Multi-line
    doc string
    \"\"\"
    for index in range(1, x):
        blah = '''
            thing'''
        # about to print
        print(index)
"""

repl = """\
>>> a = 1
>>> b = 2
>>> c = 3
"""

actions = (
    ActionsBuilder(screen, "con")
    .append(text=function)
    .switch_to_code_box(1)
    .append(text=repl)
    .wait()
    .switch_to_code_box(0)
    .suffix(1, "s")
    .suffix(1, " # append")
    .suffix(2, " # append")
    .suffix(3, " more string now")
    .suffix(5, " # append")
    .suffix(6, " # append")
    .suffix(7, "  inside blah mline")
    .suffix(8, " # append")
    .suffix(9, " more comment")
    .suffix(10, " # append")
    .wait()
    .switch_to_code_box(1)
    .suffix_typewriter(2, "9")
    .wait()
)

repl = ">>> d = 4"
multiline_repl = """\
>>> e = 5
>>> f = 6
"""

(
    actions.switch_to_code_box(1)
    .replace(3, repl)
    .wait()
    .suffix_typewriter(1, "56789")
    .wait()
    .suffix(1, "333")
    .suffix_typewriter(1, "444")
    .wait()
    .remove(2, 1)
    .insert_typewriter(2, multiline_repl)
    .insert_typewriter(0, multiline_repl)
)

if __name__ == "__main__":
    screen.run(actions)
