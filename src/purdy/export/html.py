from purdy.parser import token_ancestor, HighlightOn, HighlightOff
from purdy.themes.html import THEMES, ANCESTORS

def listing_to_html(listing, snippet=False):
    output = []

    if not snippet:
        # Full document mode
        output.append('<!doctype html>\n')
        output.append('<html lang="en">\n')
        output.append('<body>\n')

    output.append(
        '  <div style="background :#f8f8f8; overflow:auto; '
        'width:auto; border:solid gray; border-width:.1em .1em .1em .8em; '
        'padding:.2em .6em;">\n'
    )
    output.append('    <pre style="margin: 0; line-height:125%">\n')

    for line in listing:
        theme = THEMES[line.spec.name]
        ancestors = ANCESTORS[line.spec.name]
        bg = theme['Background']

        for part in line.parts:
            # For HighlightOn/Off, ignore the text content, just change the
            # background value
            #
            # This code is here because HighlightOn/Off aren't in the THEME,
            # need to work directly with the part.token, not the ancestor
            if part.token == HighlightOn:
                bg = theme["Highlight"]
                continue
            elif part.token == HighlightOff:
                bg = theme["Background"]
                continue

            token = token_ancestor(part.token, ancestors)
            fg = theme[token]

            output.append(f'<span style="{bg}{fg}">{part.text}</span>')

        output.append("\n")

    output.append("    </pre>\n")
    output.append("  </div>\n")

    if not snippet:
        output.append("</body>\n")
        output.append("</html>\n")

    return "".join(output)
