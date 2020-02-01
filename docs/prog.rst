Programming with purdy
======================

In addition to the easy to use command-line script, you can also write
programs using the purdy library. The purdy command-line script uses this
library to display a simple file to the screen. 


Example Program
---------------

.. code-block:: python

    # reads 'my_code.py' and displays it to the screen with line numbers

    from purdy.actions import AppendAll
    from purdy.content import CodeFile
    from purdy.ui import Screen

    # Screen is the entry to showing content
    screen = Screen(show_line_numbers=True)

    # Screen has one display area called "code_box", your actions need access
    # to this to write the code
    code_box = screen.code_box

    # read 'my_code.py' and parse it using the Python 3 lexer
    blob = CodeFile('my_code.py', 'py3')

    # actions are like slides in the slides show that is purdy
    actions = [
        # append the contents of the blob to the display code box
        AppendAll(code_box, blob),
    ]

    # start the display event loop
    screen.run(actions)


Every purdy library program needs to create a 
:class:`Screen <purdy.ui.Screen>` or one of its children. The Screen is what 
controls the display.  :class:`Screen <purdy.ui.Screen>` and its children 
provide one or more :class:`CodeBox <purdy.ui.CodeBox>` objects which is a
widget on the screen that displays code. 

Purdy is built using the `urwid <http://urwid.org/>`_ xterm library. 


Sample Code
-----------

Sample code can be found in the "extras/samples" directory of the repository:
https://github.com/cltrudeau/purdy/tree/master/extras/samples
