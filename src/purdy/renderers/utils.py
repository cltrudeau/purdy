# renderers/utils.py

from purdy.parser import token_ancestor

# ==============================================================================

def format_setup(no_colour, theme, themes):
    if no_colour:
        return None, None

    if isinstance(theme, str):
        theme = themes[theme]

    ancestor_list = theme.keys()

    return theme, ancestor_list

def percent_s_formatter(code, theme, ancestor_list):
    result = ""
    for line in code:
        for part in line.parts:
            if theme is None:
                result += part.text
            else:
                token = token_ancestor(part.token, ancestor_list)
                marker = theme[token]
                if marker:
                    if "%s" in marker:
                        result += marker % part.text
                    else:
                        result += marker + part.text
                else:
                    result += part.text

        if line.has_newline:
            result += "\n"

    return result
