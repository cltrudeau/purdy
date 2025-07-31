# renderers/plain.py

def to_plain(motif):
    """Transforms tokenized content in a :class:`Code` object into a plain
    text string.

    :param code: `Code` object to translate
    """
    code = motif.decorate()

    result = ""
    for line in code:
        for part in line.parts:
            result += part.text

        if line.has_newline:
            result += "\n"

    return result
