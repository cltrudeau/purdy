def listing_to_text(listing):
    """Exports a :class:`purdy.content.Listing` object to plain text."""
    output = []
    for line in listing:
        output.append(''.join([part.text for part in line.parts]))

    return "\n".join(output) + "\n"


def listing_to_tokens(listing):
    """Exports a :class:`purdy.content.Listing` object to text including its
    tokens. Kind of like Word Perfect's "show tags".
    """

    result = []
    for line in listing:
        pieces = [f"({part.token}){part.text}" for part in line.parts]
        result.append(''.join(pieces))

    return "\n".join(result) + "\n"


def listing_to_tokens_outline(listing):
    """Exports a :class:`purdy.content.Listing` object to text, with each line
    containing a single :class:`purdy.parser.CodePart` and "[EOL]" as a marker
    between lines.
    """
    longest = 0
    for line in listing:
        for part in line.parts:
            longest = max(longest, len(str(part.token)))

    longest += 2

    result = [(
        f"Lexer: '{listing.lines[0].spec.name}' "
        f"{listing.lines[0].spec.description}"
    )]
    for line in listing:
        for part in line.parts:
            token = f"({part.token})"
            result.append( f"{token:>{longest}} {part.text}" )

        result.append("[EOL]")

    return "\n".join(result) + "\n"
