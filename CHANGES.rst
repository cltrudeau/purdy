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
