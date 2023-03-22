#!/usr/bin/env python

### Example purdy library code
#
# Appends the same colourized Python REPL session to the screen multiple
# times, waiting for a keypress between each

from purdy.actions import Append, AppendTypewriter, Pause, Wait
from purdy.content import Code
from purdy.ui import SimpleScreen

screen = SimpleScreen()
code_box = screen.code_box

text = """\
# This will be appended
Antici....
...pation
# Press a key
"""

rocky = Code(text=text)

text = """\
$ pip install realpython-reader
Obtaining file:///Users/ctrudeau/code/realpython-reader-1.1.1
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build editable ... done
  Preparing editable metadata (pyproject.toml) ... done
Requirement already satisfied: feedparser
Requirement already satisfied: html2text
Requirement already satisfied: sgmllib3k
Building wheels for collected packages: realpython-reader
  Building editable for realpython-reader (pyproject.toml) ... done
  Created wheel for realpython-reader: filename=realpython_reader-1.1.1-0.editable-py3-none-any.whl size=4663 sha256=4235df475f173c3561dea3d56d21fd4ef96f9c950b0807c53ca8aa69395fc9f5
  Stored in directory: /private/var/folders/mz/5txqv6hs4232hkjbxcny3jt40000gn/T/pip-ephem-wheel-cache-xxyt67v3/wheels/96/1f/e4/96bcd125f56372f550bb71af8c24b1144687c854f32e988e4b
Successfully built realpython-reader
Installing collected packages: realpython-reader
  Attempting uninstall: realpython-reader
    Found existing installation: realpython-reader 1.1.1
    Uninstalling realpython-reader-1.1.1:
      Successfully uninstalled realpython-reader-1.1.1
Successfully installed realpython-reader-1.1.1
"""

install = Code(text=text, lexer_name='bash')

actions = [
    Append(code_box, rocky, pauses=[Pause(2, 1), ]),
    Wait(),
    AppendTypewriter(code_box, install, pauses=[Pause(6, 1), Pause(14, 1)]),
]

if __name__ == '__main__':
    screen.run(actions)
