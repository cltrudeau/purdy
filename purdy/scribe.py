"""
Scribe Module (purdy.scribe.py)
===============================

Methods for transforming code into different representations on stdout.
"""
from colored import fg, bg, attr

from purdy.colour import COLOURIZERS

RTFColourizer = COLOURIZERS['rtf']

# =============================================================================
# Utility Methods
# =============================================================================

def range_set_to_list(text):
    ### converts a range set of numbers to a sorted list of unique numbers
    #
    # e.g: 3-5,9,8,4 => [3, 4, 5, 8, 9]
    values = set()
    parts = text.split(',')
    for part in parts:
        if '-' in part:
            start, stop = part.split('-')
            start = int(start)
            stop = int(stop) + 1
            values.update(range(start, stop))
        else:
            values.add(int(part))

    return sorted(values)

# =============================================================================
# Scribe to <stdout> Methods
# =============================================================================

def print_tokens(listing, colour=True):
    """Prints each line in a :class:`purdy.content.Code` object with a
    coloured background, then prints the parsed tokens inside that line

    :param listing: :class:`purdy.content.Listing` object containing code to
                    print

    :param colour: set to True to print out using ANSI colour. Defaults to True
    """
    for line in listing.lines:
        text = line.text
        if text == '':
            text = '\\n'

        if colour:
            print(fg('white') + attr('bold') + bg('blue') + text +attr('reset'))
        else:
            print(text)

        for part in line.parts:
            output = part.text
            if output == '':
                output = "''"

            if colour:
                if output != "''":
                    output = fg('black') + bg('grey_70') + output +attr('reset')

                print(f'    {part.token}: {output}')
            else:
                if output == '':
                    output = "''"
                print(f'    {part.token}: {output}')

# -----------------------------------------------------------------------------

def print_ansi(listing):
    for row in listing.content():
        print(row)

# -----------------------------------------------------------------------------

def print_html(listing, snippet=True):
    """Prints the code in an HTML representation.

    :param listing: :class:`Listing` object containing code to print
    :param snippet: if True, prints out just the <div> containing the code.
                    Otherwise, prints a full valid HTML file. Defaults to
                    True.
    """
    output = []
    if not snippet:
        output.extend([
            '<!doctype html>',
            '<html lang="en">',
            '<body>',
        ])

    output.append( ('<div style="background :#f8f8f8; overflow:auto; '
        'width:auto; border:solid gray; border-width:.1em .1em .1em .8em; '
        'padding:.2em .6em;"><pre style="margin: 0; line-height:125%">')
    )

    for row in listing.content():
        output.append( row + '\n')

    output.append('</pre></div>\n')

    if not snippet:
        output.append('</body>\n</html>')
    print(''.join(output))

# -----------------------------------------------------------------------------

def print_rtf(listing, background_colour=None):
    """Prints an RTF document containing the colourized code

    :param listing: :class:`Listing` object containing code to print
    """
    if background_colour:
        listing.colourizer.set_background_colour(background_colour)

    output = [listing.colourizer.rtf_header, ]

    for row in listing.content():
        output.append(row)
        output.append('\\\n')   # \ is rtf newline

    output.append('}')
    print(''.join(output))
