#!/usr/bin/env python

from purdy.actions import AppendTypewriter
from purdy.settings import settings
from purdy.content import Code
from purdy.ui import SimpleScreen

settings['movie_mode'] = 200

screen = SimpleScreen(settings)
code_box = screen.code_box
blob = Code('../display_code/console2.repl')
action = AppendTypewriter(code_box, blob)
screen.run([action])
