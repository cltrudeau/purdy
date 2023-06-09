import struct

from purdy.parser import token_ancestor, HighlightOn, HighlightOff
from purdy.themes.rtf import THEMES, ANCESTORS

# =============================================================================

class RTFHeaders:
    # RTF Uses a lot of slashes, use r-strings

    preamble = (
        r"{\rtf1\ansi\ansicpg1252" + "\n"
        r"{\fonttbl\f0\fnil\fcharset0 RobotoMono-Regular;}" + "\n"
    )

    # Colour table is all one line (no newlines), has a placeholder for an
    # extra colour at the end
    color_table = (
        r"{\colortbl;"
        r"\red255\green255\blue255;"
        r"\red143\green89\blue2;"
        r"\red32\green72\blue167;"
        r"\red206\green92\blue0;"
        r"\red0\green0\blue0;"
        r"\red52\green101\blue164;"
        r"\red204\green0\blue0;"
        r"\red92\green53\blue204;"
        r"\red78\green154\blue6;"
        r"\red0\green0\blue207;"
        r"\red239\green41\blue41;"
        r"\red164\green0\blue0;"
        r"\red213\green213\blue213;%s}"
    )

    font_spec = r'\f0\fs28' + '\n'

# =============================================================================
# RTF Utilities
# =============================================================================

def rtf_encode(text):
    """RTF uses a weird UTF-16 decimal escape sequence for encoding unicode.
    This method take a string and returns an RTF encoded version of it."""
    output = []
    data = text.encode('utf-16le')
    length = len(data) // 2

    # use struct.unpack to turn the pairs of bytes into decimal unicode escape
    # numbers
    parts = struct.unpack(f'<{length}H', data)
    index = 0
    size = len(parts)

    while index < size:
        num = parts[index]

        if num <= 127:
            # regular ascii
            letter = chr(num)

            # Escape characters that are used by RTF
            if letter == '\\':
                output.append('\\\\')
            elif letter in '{}':
                output.append('\\' + letter)
            else:
                output.append(letter)
        elif num <= 256:
            # extended ascii, use hex notation
            output.append(f"\\'{num:2x}" )
        elif num < 55296:
            # 0xD800 (55296) is the the boundary for two-word encoding, less
            # than this means it is a single item
            output.append(f"\\uc0\\u{num}")
        else:
            # greater than 0xD800, means two words
            index += 1
            next_num = parts[index]
            output.append(f"\\uc0\\u{num} \\u{next_num}")

        index += 1

    return ''.join(output)

def hex_colour_to_rtf(colour):
    """Converts an HTML style hex colour string to the three component colour
    indicator used in an RTF colour table.

    :param colour: string containing a HTML hex colour code without the
                   starting #, e.g. "ccc", "f3b2e1"
    """
    double_it = lambda s, i: f'0x{s[i]}{s[i]}'

    # calculate the integer value of the hex colour
    if len(colour) == 3:
        red = int(double_it(colour, 0), base=16)
        green = int(double_it(colour, 1), base=16)
        blue = int(double_it(colour, 2), base=16)
    else:
        red = int(f'0x{colour[0:2]}', base=16)
        green = int(f'0x{colour[2:4]}', base=16)
        blue = int(f'0x{colour[4:6]}', base=16)

    return f'\\red{red}\\green{green}\\blue{blue};'  # rtf colour descriptor

# =============================================================================

def listing_to_rtf(listing, background=None):
    # Create RTF document header and colour table
    output = [ RTFHeaders.preamble ]

    bg_rgb = ''
    bg = THEMES[listing.lines[0].spec.name]['Background']
    if background is not None:
        # Custom background colour gets added to the colour table, it is entry
        # 14, so store the value to insert in the table, and set the bg colour
        # to be the 14th
        bg_rgb = hex_colour_to_rtf(background)
        bg = "\\cb14\n"

    output.append(RTFHeaders.color_table % bg_rgb)
    output.append(RTFHeaders.font_spec)
    output.append(bg)

    # Write the document contents
    for line in listing:
        theme = THEMES[line.spec.name]
        ancestors = ANCESTORS[line.spec.name]

        for part in line.parts:
            # For HighlightOn/Off, ignore the text content, just change the
            # background value
            #
            # This code is here because HighlightOn/Off aren't in the THEME,
            # need to work directly with the part.token, not the ancestor
            if part.token == HighlightOn:
                output.append(theme["Highlight"])
                continue
            elif part.token == HighlightOff:
                output.append(bg)
                continue

            token = token_ancestor(part.token, ancestors)
            output.append( theme[token] % part.text )

        output.append('\\\n')   # \ is rtf newline

    # Close RTF doc
    output.append("}")

    return "".join(output)
