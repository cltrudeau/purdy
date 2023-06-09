import colored

from purdy.parser import token_ancestor, HighlightOn, HighlightOff
from purdy.themes.ansi import THEMES, ANCESTORS

get_code = lambda fn, colour: '' if not colour else fn(colour)
reset = colored.attr('reset')

def listing_to_ansi(listing):
    output = []

    for line in listing:
        theme = THEMES[line.spec.name]
        bg = get_code(colored.bg, theme['Background'])
        ancestors = ANCESTORS[line.spec.name]

        for part in line.parts:
            # For HighlightOn/Off, ignore the text content, just change the
            # background value
            #
            # This code is here because HighlightOn/Off aren't in the THEME,
            # need to work directly with the part.token, not the ancestor
            if part.token == HighlightOn:
                bg = get_code(colored.bg, theme['Highlight'])
                continue
            elif part.token == HighlightOff:
                bg = get_code(colored.bg, theme['Background'])
                continue

            token = token_ancestor(part.token, ancestors)

            # Not a highlighting token
            if isinstance(theme[token], tuple):
                fg = get_code(colored.fg, theme[token][0])
                attr = get_code(colored.attr, theme[token][1])
            else:
                fg = get_code(colored.fg, theme[token])
                attr = ''

            output.append(f"{fg}{attr}{bg}{part.text}{reset}")

        output.append("\n")

    return ''.join(output)


def listing_to_tokens_ansi(listing):
    """Exports a :class:`purdy.content.Listing` object to text, with each line
    containing a single :class:`purdy.parser.CodePart` and "[EOL]" as a marker
    between lines, using colourized output.
    """
    result = [(
        f"Lexer: '{listing.lines[0].spec.name}' "
        f"{listing.lines[0].spec.description}"
    )]

    longest = 0
    for line in listing:
        for part in line.parts:
            longest = max(longest, len(str(part.token)))

    longest += 2

    bg = get_code(colored.bg, 'grey_19')

    for line in listing:
        theme = THEMES[line.spec.name]
        ancestors = ANCESTORS[line.spec.name]

        for part in line.parts:
            token = token_ancestor(part.token, ancestors)
            if isinstance(theme[token], tuple):
                fg = get_code(colored.fg, theme[token][0])
                attr = get_code(colored.attr, theme[token][1])
            else:
                fg = get_code(colored.fg, theme[token])
                attr = ''

            display = f"({part.token})"
            result.append(
                f"{display:>{longest}} {fg}{attr}{bg}{part.text}{reset}" )

        result.append("[EOL]")

    return "\n".join(result) + "\n"
