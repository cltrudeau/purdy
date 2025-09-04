# code_api.py
#
# Shows how to use the `Code` class to combine and build content of different
# types then display it to the screen

from purdy.content import Code
from purdy.renderers import to_rich

# =============================================================================

CONSOLE = """\
$ python
Python 4.2 (Pretending to be an interpreter"
"""

code = Code.text(CONSOLE, "con")

code.append(">>> print('hello')\nhello", "repl")
code.append("\n>>> print('")
code.append_token("goodbye")
code.append("')\ngoodbye")


