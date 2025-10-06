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

    from purdy.tui import AppFactory, Code

    # An app is the entry to showing content. The AppFactory has convenience
    # methods for creating an app.
    app = AppFactory.simple(line_number=1)

    # A `CodeBox` object is what displays your content to the screen. A simple
    # app has one of these called `box`
    box = app.box

    # Read a file and parse it using the `Code` object
    code = Code('my_code.py')

    # You perform actions on the `CodeBox` by chaining calls. These calls
    # effect how things are presented.
    (box
        .append(code)
        .set_numbers(1)
    )

    # Purdy is a Textual app, so you run it like you would any Textual program
    app.run()

Purdy is a Textual app, and the :class:`purdy.tui.apps.AppFactory` is a
convenient way to to create an app instance. Inside the app, you can have one
or more :class:`purdy.tui.codebox.CodeBox` objects that display contents. The
:func:`purdy.tui.apps.AppFactory.simple` call creates a single `CodeBox` that
fills the screen.  :func:`purdy.tui.apps.AppFactory.split` creates a screen
with two boxes one above the other.

You put content in a `CodeBox` using a :class:`purdy.content.Code` object. The
`Code` object constructor takes the name of a file to read. By default it
attempts to detect what kind of content is in the file based on the file
extension. There is a long list of extensions supported, each providing their
own syntax highlighting. The three most common are `.py` for Python files,
`.repl` for text captures of a Python REPL session, and `.con` for Bash shell
sessions. A full list of supported file names can be found by running the
`purdy` command without arguments.

The `Code` object also has a :func:`purdy.content.Code.text` method that can
be used as a factory that parses a string. This method assumes the string
contains Python code, but you can use the `lexer` argument to specify other
kinds of content.

In addition to adding `Code` objects to the `CodeBox`, you can also add text
in the form of `Textual Markup
<https://textual.textualize.io/guide/content/#markup/>`_. If you only want
plain text, the :class:`purdy.tui.tui_content.EscapeText` wrapper escapes the
Textual Markup.

Once you have created an app, you access its `CodeBox` objects and perform
actions on them. Actions change what you see on the screen. Two common actions
are :func:`purdy.tui.codebox.CodeBox.append` which appends text to the box, and
:func:`purdy.tui.codebox.CodeBox.typewriter` which animations typing of the
content. If the content type being animated represents an interactive console,
the typewriter animation will wait at each prompt, allowing you to control the
pace of the animation. In Python, `>>>` and `...` are considered prompts, and
in Bash anything starting with `$` is one.

Actions all return an instance of the `CodeBox` that called them, so can be
chained together.

View more examples in the :ref:`code-samples` section.

---------------------------------------------------------------------------

Library API
###########

.. autoclass:: purdy.tui.apps.AppFactory
    :members:

.. autoclass:: purdy.content.Code
    :members:

.. autoclass:: purdy.content.PyText
    :members:

.. autoclass:: purdy.themes.Theme
    :members:

.. automodule:: purdy.tui.codebox
    :members: CodeBox, BoxSpec, RowSpec
