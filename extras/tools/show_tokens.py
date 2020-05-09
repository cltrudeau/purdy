#!/usr/bin/env python

import argparse

from purdy.content import LEXERS, Code

# =============================================================================

def colour_print(text, bw):
    if bw:
        print(text)
    else:
        from ansi.colour import bg
        print( bg.blue(text) )

# =============================================================================

lexer_choices = ', '.join([f'{key}:{name}' for key, name in LEXERS.choices])

parser = argparse.ArgumentParser(description=('Prints out each line in a '
    'file with the corresponding tokens indented beneath it'))

help_text = 'Name of lexer to use to parse the file. Choices are: ' + \
    lexer_choices + '. Defaults to "py3"'

parser.add_argument('-l', '--lexer', help=help_text, default='py3')
parser.add_argument('--bw', help=('By default code lines are highlighted ' 
    'using ANSI colour. This flag turns this off.'), action='store_true')
parser.add_argument('files', type=str, nargs='+',
    help='One or more file names to parse')

args = parser.parse_args()

# --- Do the parsing

for filename in args.files:
    code = Code(args.lexer, content_filename=filename)
    for line in code.lines:
        colour_print(line.text, args.bw)
        for token in line.tokens:
            print(f'    {token.token_type}: {token.text}')
