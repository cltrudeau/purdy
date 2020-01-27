#!/usr/bin/env python

# Example code for programatically calling the purdy library and showing a
# console based code snippet

from pathlib import Path

from purdy.conf import settings
from purdy.ui import purdy_window

path = Path('../display_code/console.py')
contents = path.read_text()

purdy_window(contents)
