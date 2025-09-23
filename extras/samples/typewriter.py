#!/usr/bin/env python
# features.py
#
# Shows off the main features of the purdy coding interface
from purdy.tui import AppFactory, Code, EscapeText, TextSection

# =============================================================================

app = AppFactory.simple(auto_scroll=True)
box = app.box

INTRO = """\
[on blue]Typewriter demo[/]

Press right arrow to show the next animation step →

"""

repl = Code("../display_code/short.repl")

# Intro
(box
    .append(INTRO)
    .wait()
    .text_typewriter(EscapeText("plain text [no markup]"))
    .wait()
    .set_numbers(1)
    .append("Turned numbering on")
    .wait()
    .text_typewriter(
        TextSection(["multi-line mixed", EscapeText("with [escaped] text")])
    )
    .wait()
    .text_typewriter("some [green]markup[/] text")
    .wait()
    .text_typewriter(
        TextSection(["[yellow]multi-line[/]", "markup [green]text[/] section"])
    )
    .wait()
    .typewriter(repl)
)

app.run()
