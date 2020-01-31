purdy
*****

During talks or screencasts I don't want to be typing code, it is too error
prone and too likely to mess up my speaking flow. "purdy" takes snippets of
code and displays them to a terminal using Pygments colourization. It listens
for input and shows a line as if it is being typed each time you press enter.

Example Usage:

.. code-block:: bash

    $ purdy code-snippet.py

Running the above command will clear the console and start typing the code
snippet. Output is paused when it sees a REPL prompt (">>> "). Pressing any
key (except "q") will continue the typing. Lines starting with a prompt mimic
typing, lines not on a prompt are output immediately.

.. image:: example_purdy.gif

Once the code has been displayed, further key presses are ignored. At any time
you can press "q" to quit.


Command Line Options
====================

-c, --continuous
    Instead of waiting for key presses, display the whole file

-x16
    purdy defaults to using 256 colour mode in the terminal. This flag forces
    it to use 16 colour mode

-l, --lexer
    Default lexer is Python Console lexer ('con'), using this parameter you
    can also change it to a Python 3 code lexer ('py3')

-d, --delay DELAY
    change the amount of delay between "typed" letters. Defaults to 130ms.
    Value given in milliseconds. Mutually exclusive with the "--wpm" option

-w, --wpm WPM
    specify the typing speed in Words Per Minute. Mutually exclusive with the
    "--delay" option

--variance VARIANCE
    to make the typing look more real a random value of plus or minus
    "VARIANCE" is added to the typing delay.  Default value for this is 30ms.
    Value given in milliseconds.

--version
    Display pgraom version and exit

--help
    Display help information


Installation
============

.. code-block:: bash

    $ pip install purdy


Coding With Purdy
=================

The "purdy" script is fairly simple. You can also create programs using the
purdy library. Your programs can have much more complicated interactions,
including having split screens, highlighting lines and more. 


Supports
========

purdy has been tested with Python 3.7


Docs & Source
=============

Docs: http://purdy.readthedocs.io/en/latest/

Source: https://github.com/cltrudeau/purdy
