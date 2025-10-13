*****
Purdy
*****

During talks or screencasts I don't want to be typing code, it is too error
prone and too likely to mess up my speaking flow. **Purdy** is both a set of
programs and a library to display colourized code in a series of animations.

The ``purdy`` command displays your program or data to screen with
colourization. It supports a number of syntax highlighters including Python,
Python REPL, Bash console and more.  Source code can be presented to the
screen as if typing.  For console files, the typing pauses at a prompt,
waiting for interaction.  Prompts are:

* ``>>>`` or ``...`` for Python REPL
* ``$`` for Bash console

If the program is paused at a prompt, pressing the **right** arrow will
continue. Typing animation can be skipped over by pressing the letter "s"
instead. Animation can be undone by pressing the **left** arrow. More info on
keys can be found in the help dialog, viewed by pressing "h".

Example Usage:

.. code-block:: bash

    $ purdy code-snippet.py

The result looks like this:

.. image:: screenshot.gif

Once the code has been displayed, further key presses are ignored. At any time
you can press "q" to quit.


Purdy Programs
##############


The following programs come with the `purdy` library:

* ``purdy`` -- Animated display that looks like a program is being typed to the
  screen.
* ``subpurdy`` -- Full set of commands to control Purdy. Sub-commands dictate
  behaviour, doing a variety of code presentation. Includes ANSI, RTF, HTML
  output as well as the typewriter animations.

More information can be found in the Command Line Program Documentation.


Purdy TUI Controls
##################

The following keys help you to control the TUI purdy programs:

* ``h`` -- Help screen
* ``<RIGHT>`` -- next animation step
* ``<LEFT>`` -- previous animation step
* ``s`` -- go to the next step, skipping any animation

For custom made code using the purdy library, the following controls will also
work:

* ``<TAB>`` -- focus next window area in a multi Screen display
* ``<SHIFT><TAB>`` -- focus previous window area in a multi Screen display

Additionally the ``s``, and ``<LEFT>`` commands all support skipping multiple
steps by specifying a number first. For example the sequence ``12s`` would
skip past the next 12 steps.


Purdy Library
#############

The ``purdy`` script is fairly simple, but you can create more complex
animations by writing programs using the purdy library. Custom programs can
have split screens, highlight lines, do slide transitions, and more.  More
information can be found in the Library Documentation.


Installation
############

.. code-block:: bash

    $ pip install purdy


Supports
########

Purdy has been tested with Python 3.13. Terminal control is done with the
`Textual <https://github.com/Textualize/textual>`_ library. Parsing and
tokenization is done through `Pygments <https://pygments.org/>`_. Both
libraries are excellent and I'm grateful they're publicly available.

Purdy was re-written from the ground up for version 2, moving to Textual and
doing an API redesign based on pain points over the years. Version 2 is not
compatible with version 1 which was based on `Urwid <http://urwid.org/>`_. For
the deprecated version see the `purdy 1 branch
<https://github.com/cltrudeau/purdy/tree/purdy1>`_ or ``pip install
purdy==1.14.1``.

Docs & Source
#############

Docs: http://purdy.readthedocs.io/en/latest/

Source: https://github.com/cltrudeau/purdy
