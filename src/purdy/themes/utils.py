from purdy.parser import _built_in_specs

def spawn_themes(**kwargs):
    # Returns two things: a THEMES dictionary and an ANCESTOR dictionary.
    #
    # THEMES dictionary combines the dictionaries passed in as kwargs along
    # with defaults for each lexer type based on the style (at minimum the
    # kwargs must contain mappings for the styles)
    #
    # ANCESTORS is the list of ancestors of the tokens used in the themes

    themes = {}
    ancestors = {}
    for name, value in kwargs.items():
        themes[name] = value
        ancestors[name] = value.keys()

    for spec in _built_in_specs:
        if spec.name not in themes:
            themes[spec.name] = themes[spec.style]
            ancestors[spec.name] = themes[spec.style].keys()

    return themes, ancestors
