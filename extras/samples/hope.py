# mixed.py
from purdy.tui import AppFactory, Code, TText

# =============================================================================

CONTENT = """This is some babbling text which will appear in a bunch of different colours. I'll just keep typing for a while. That should be enough I would think, yes?  """

app = AppFactory.simple()
box = app.box

text = """\
$ python
Python 3.13.5 (v3.13.5:6cb20a219a8, Jun 11 2025, 12:23:45)
Type "help", "copyright", "credits" or "license" for more information.
"""

con = Code.text(text, theme_name="foo")
repl = Code("../display_code/console.repl", theme_name="bar")
code = Code("../display_code/code.py")

(box
    .append(con)
    .append_typewriter(repl)
    .wait()
    .transition(code[0:2])
    .wait()
    .highlight_chain(0, 1, 2)
    .wait()
    .set_line_numbers()
    .append(code[3:])
)

###
# 1) Show the bash script
# 2) Typewriter the REPL script, going through a series of prompts
# 3) Clear the internal representation and replace it with the first 3 lines
# of the `code` variable
# 4) Series of highlights on/off inside internal representation
# 5) Turn line numbers on inside internal representation
# 6) Append another code segment to internal representation

app.run()
