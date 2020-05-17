.. _library-documentation:

Library Documentation
#####################

In addition to the easy to use command-line script, you can also write
programs using the purdy library. The purdy command-line script uses this
library to display a simple file to the screen. 


Example Program
===============

.. code-block:: python

    # reads 'my_code.py' and displays it to the screen with line numbers

    from purdy.actions import Append
    from purdy.content import Code
    from purdy.ui import SimpleScreen

    # Screen is the entry to showing content
    screen = SimpleScreen(starting_line_number=1)

    # Screen has one display area called "code_box", your actions need access
    # to this to write the code
    code_box = screen.code_box

    # read 'my_code.py' and parse it using the Python 3 lexer
    blob = Code('code.py', lexer_name='py3')

    # actions are like slides in the slides show that is purdy
    actions = [
        # append the contents of the blob to the display code box
        Append(code_box, blob),
    ]

    # start the display event loop
    screen.run(actions)


Every purdy library program needs to create a 
:class:`Screen <purdy.ui.Screen>` or one of its children. The Screen is what 
controls the display.  :class:`Screen <purdy.ui.Screen>` and its children 
provide one or more :class:`CodeBox <purdy.ui.CodeBox>` objects which is a
widget on the screen that displays code. You combine a series of 
:mod:`purdy.ui.actions` to display and alter the code. View more examples in
the :ref:`code-samples` section.

---------------------------------------------------------------------------

Library API
###########

.. automodule:: purdy.ui
    :members: Screen, SimpleScreen, SplitScreen, CodeBox, TwinCodeBox

.. automodule:: purdy.content
    :members: Code

.. automodule:: purdy.actions
    :members:
    :exclude-members: AppendTypewriter, InsertTypewriter, ReplaceTypewriter, SuffixTypewriter


Typewriter Actions
==================

Typewriter actions display code using a typewriter animation. Code content is
displayed a letter at a time as if someone is typing. The
:mod:`purdy.settings` module contains default values for typing speeds and
variance time between letters being pressed.

When the code in question is based on a console, the typewriter will wait for
a the `right arrow` to be pressed whenever it sees a prompt. For example, when
appending Python REPL code, the ``>>>`` will cause the interface to wait.

.. autoclass:: purdy.actions.AppendTypewriter
    :members:

.. autoclass:: purdy.actions.InsertTypewriter
    :members:

.. autoclass:: purdy.actions.ReplaceTypewriter
    :members:

.. autoclass:: purdy.actions.SuffixTypewriter
    :members:


Default Settings
================

.. autoattribute:: purdy.settings.settings
    :annotation:

.. literalinclude:: ../purdy/settings.py
    :language: python
