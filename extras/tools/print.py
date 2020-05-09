#!/usr/bin/env python

### Command line script that uses the colored library to print the given file
# to the screen, colorized

import argparse

from purdy.content import LEXERS, TokenLookup

# =============================================================================
# Main
# =============================================================================

colours = {
    'black':'30',
    'dark red':'31',
    'dark green':'32',
    'brown':'33',
    'dark blue':'34',
    'dark magenta':'35',
    'dark cyan':'36',
    'light gray':'37',
    'dark gray':'30;1',
    'light red':'31;1',
    'light green':'32;1',
    'yellow':'33;1',
    'light blue':'34;1',
    'light magenta':'35;1',
    'light cyan':'36;1',
    'white':'37;1',
}

def colourize(name, text):
    if not name:
        return text

    global colours
    code = colours[name]
    return f'\033[{code}m{text}\033[0m'

if __name__ == '__main__':
    # define command line arguments
    parser = argparse.ArgumentParser(description=('Prints a colorized '
        'version of a python file'))

    parser.add_argument('filename', help=('Name of file containing python to '
        'parse'))

    parser.add_argument('-l', '--lexer', choices=LEXERS.choices,
        default='py3', help=('Choose Pygments Lexer to use to parse the '
        'content. Choices are "con" for console, or "py3" (default) for '
        'Python 3'))

    # --- 
    args = parser.parse_args()

    lexer = LEXERS.get_lexer(args.lexer)
    with open(args.filename) as f:
        contents = f.read()
        for token_type, text in lexer.get_tokens(contents):
            # find the colour for this token
            token = TokenLookup.get_coloured_token(token_type)
            colour = TokenLookup.get_colour_attribute(token)[1]

            print(colourize(colour, text), end='')
