#!/usr/bin/env python

import argparse

from pygments.lexers import BashSessionLexer

# =============================================================================

parser = argparse.ArgumentParser(description=('Prints out the tokens ' 
    'generated by pygments.lexers.BashSessionLexer'))
parser.add_argument('files', type=str, nargs='+',
    help='One or more file names to lex and parse')

args = parser.parse_args()

# --- Do the parsing

lexer = BashSessionLexer()
with open(args.files[0]) as f:
    contents = f.read()

for token, text in lexer.get_tokens(contents):
    if text == '\n':
        text = '\\n'

    print('%s: %s' % (token, text))
