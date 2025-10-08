2.0.0b2
=======

* 2025/10/??
* Changed textual markup code highlighting so inner tokens are rendered plain,
  reversing the coloured ones was ugly
* Slowed down the move_by animation
* Add ability to partial highlight based on function's argument number
* Add Python source code manipulation tools: find a subset by name, remove
  double blanks, and left justify
* Fix bug with starting line numbers not getting initialized


2.0.0b1
=======

* 2025/10/01
* Add purdy command
* Add full documentation and fixed pydoc inter-class references
* Dead code removal


2.0.0a6
=======

* 2025/09/29
* overhauled when things get rendered and how to greatly reduce load time
* add `.highlight_chain`
* moved all UI components into a single parent container so that purdy can be
  used as a widget
* Added optional title to CodeWidget
* Added `.move_by()` scroll control action


2.0.0a5
========

* 2025/09/10
* Fix packaging problem that failed to include .tcss file

2.0.0a4
========

* 2025/09/10
* Updates to typewriter so it handles consoles properly
* Fix bug where textual markup wasn't getting escaped properly
* Moved factory functions into a common AppFactory class
* Added things you need for the code API into tui/__init__ so you only need to
  know about one import

2.0.0a3
========

* !!! BREAKING CHANGE RELEASE
* 2025/09/08
* A complete ground-up re-write using Textual as the tui (URWID was
  problematic)
* Absolutely nothing is compatible with the old version, the programming
  interface has changed drastically
* Some of the command line tools will be similar but if you coded against the
  API your old code won't work with this version

1.14.1
======

* 2025/04/13
* Fixed bug where long line wraps for AppendTypewriter weren't scrolling the
  screen
* Pygments has changed how it parses certain text, bumped min requirement for
  consistency

1.14
====

* 2024/11/07
* Add ability to use plain text in Insert and Append actions
* Fix bug where "none" lexer was adding an extra newline
* Add support for Python 3.13
* Remove support for Python 3.8

1.13.3
======

* Fix bug where HighlightChain wasn't turning off
* Changed tox tests to cover 3.8-3.12 (drop 3.7, add 3.12)

1.13.2
======

* Add ability to include a header when using the Code.python_portion() method
* Update requirements bounds to avoid a breaking change from colored==2.0.0


1.13.1
======

* The "none" lexer added in 1.11 used Pygment's TextLexer which returns all
  text as a single blob, rather than splitting it by lines. Added a new
  internal lexer that lexes on newlines and switched the "none" parser to use
  it

1.13
====

* Add new action that simulates a prompt and a response


1.12
====

* Add ability to add pauses during console output for Insert, Append, and
  their typewriter equivalents

1.11
====

* Added lexers for a variety of document formats: YAML, RST, Markdown
* Added a lexer for no tokenization
* Updated minimum Pygments version to 2.14

1.10.2
======

* Added 3.11 testing to tox, removed 3.6

1.10.1
======

* Simplified DollarBashSessionLexer by removing special handling of comment
character which can be put after the prompt line if required. Makes code a lot
closer to Pygments base and less likely to break

1.10.0
======

* Add DollarBashSessionLexer, with special handling for Bash session prompts
to do better highlighting if your prompt uses a dollar sign
* Upgrade dependency to Pygments==2.10.0 to use their NodeConsoleLexer
now that it has been contributed
* Add Python 3.10 to test suite

1.9.1
=====

* Bug fixes for the RTF generator, not escaping braces 
* Bug fixes for NodeConsoleParser, not >3 leading dots correctly

1.9.0
=====

* Add custom lexer for Node.js interactive console sessions, included it in
the PurdyLexers listing

1.8.1
=====

* bug fix: TwinBoxes weren't initializing proplery causing crashes when used
with AppendTypewriter

1.8.0
=====

* add Code.subset() method that returns a new Code object including only a 
subset of the original's source
* upgrade minimum dependency on Pygments due to security advisory

1.7.0
=====

* Added @johanvergeer's contribution of the ActionsBuilder class, a short cut
class based on a builder pattern so you can use methods on the builder class
to create actions instead of a list of actions. Supports type hinting in case
that's your thing
* Upgraded minimum version of Pygments to 2.8 due to behaviour changes in the
parser causing conflicts during testing
* Added help screen
* Added section markers and ability to skip to a section in the TUI
* Changed Sleep to accept a tuple specifying range of random amount to sleep
* Add ability to skip multiple steps, sections, or backwards steps by typing a
number before the command

1.6.1
=====

* Change base colours for URWID palette after complaints that the dark text
was hard to read against black backgrounds

1.6.0
=====

* Add ability for Transition to accept no code, so can do a screen wipe to
blank
* Add unit tests for Code source change methods
* Fix bugs found with above unit test

1.5.0
=====

* Changed how the wrapper to the pygments lexers work, the wrapper is now
responsible for choosing the palette to go with the colourizer, this means
custom colourizers for things that aren't code like (HTML, XML) can now have
different palettes from code
* Custom lexer now supports named palettes
* Add better error handling to the load action sequence
* Add error handling detecting Transitions that are missing both code and
code_box_to_copy
* Add error handling when trying to Replace outside of box boundaries
* Removed ReplaceTypewriter, multi-line replacement was ambiguous, use a
Remove and InsertTypewriter to explicitly do what you need
* Add error handling if a negative index is passed to InsertTypewriter,
updated incorrect documentation

1.4.0
=====

* Added methods to the Code object so you can manipulate the source before it
is rendered. You can add, remove and change lines; remove double spaces; and
if the source is python show only a subset like a given function

1.3.0
=====

* Code objects now support a custom lexer: with a little extra code you can
now use any Pygments lexer to parse your little heart out

1.2.5
=====

* hidden max_height feature was made accessible in the bin/purdy command line


1.2.4
=====

* fix bug in RTF formats where backslashes weren't escaped properly


1.2.3
=====

* moved command line scripts out of the module, it appeared to be messing up
  readthedocs, should have no impact on installation 

1.2.1
=====

* Fix bug where the compact parameter on CodeBox wasn't working
* Add parameter to SplitScreen to support the compact parameter in its top box

1.2.0
=====

* Added HighlightChain action
* Added VirtualCodeBox and ability to copy a VCB into a real code box through
  a Transition action
* Used the iscreen mechanism introduced in the last release to create a better
  test harness


1.1.1
=====

* Bug fix: purdy cmd wasn't launching properly due to type-o in fake args


1.1.0
=====

* Refactored how screens work, they're now a proxy for an implementation
  inside of "purdy.iscreen". The Urwid code viewer now lives in
  "purdy.iscreen.tui" and a new viewer has been added that does text export
* Added Sleep action
* Tranistion actions are now skippable
* Transition actions don't automatically trigger a Wait anymore, you have to
  call Wait explicitly

1.0.2
=====

* Bug fix: crash when Fold is called without a Wait immediately afterwards,
  urwid was caching a focus position and trying to set it to a line that
  wasn't there anymore

1.0.1
=====

* Bug fix: crash when fast-forward called on Transtion due to missing skip
  parameter

1.0
===

* Breaking change release
* Moved animation mechansim to be based on a queue, can now go forwards and
  backwards
* Signatures of Actions and Screens have changed
* Add tools for printing code in other formats such as RTF and HTML

0.4
===

* Add support for bash session lexer
* Add RowScreen type that can handle multiple rows and side-by-side pairs of
  boxes
* Add focus indicator to boxes without scroll indicators

0.3
===

* Added tool that uses coloured lexer to print code to console
* Added auto scrolling feature for the CodeBox containers
* Added new actions for inserting and editing lines

0.2
===

* Purdy can now be used as a library as well as a standalone script
* Added Python code lexer 
* Added scrollbar indicators
* Added SplitScreen
* Added line number support
* Added highlighting of lines


0.1.1
=====

* Patched documentation

0.1
===

* Initial release to pypi
