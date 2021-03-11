#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates using the ActionsBuilder instead of action classes
from purdy.builder import ActionsBuilder
from purdy.settings import settings
from purdy.ui import SplitScreen

def do_foo():
    return 'This is foo'

settings["movie_mode"] = 2
py_code = "../display_code/code.py"
con_code = "../display_code/simple.repl"

screen = SplitScreen(settings)

actions = (
    ActionsBuilder(screen, "con")
    .append(filename=py_code)
    .insert(22, text='thing.stuff(43)')
    .switch_to_code_box(1)
    .append_typewriter(filename=con_code)
    .stop_movie()
    .switch_to_code_box(0)
    .highlight(39, True)
    .replace(22, text='thing.stuff(3000)')
    .wait()
    .clear()
    .append(text="print('Hello world')")
    .suffix(1, "  # comment")
    .shell("echo 'hello'")
    .wait()
    .remove(2, 1)
    .insert_typewriter(1, text="inserting via typewriter")
    .suffix_typewriter(1, ".... more text")
    .highlight_chain([1, 2,])
    .switch_to_code_box(1)
    .fold(2, 2)
    .sleep(1)
    .transition(con_code)
    .run_function(do_foo, None)
)

if __name__ == "__main__":
    screen.run(actions)
