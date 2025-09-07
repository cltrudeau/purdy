# scribe.py
# Print Utilities

from rich.console import Console

# ==============================================================================

console = Console(highlight=False)
rprint = console.print

# ==============================================================================

def print_code_lines(lines, title="", title_enabled=True, no_colour=False):
    if title_enabled:
        console.rule(title)

    for line in lines:
        rprint( (f"CodeLine({line.lexer_spec.lexer_cls.__name__}, "
            f"{line.has_newline}") )
        for part in line.parts:
            output = "   "
            if not no_colour:
                output += "[reverse]"

            output += part.text

            if not no_colour:
                output += "[/]"

            output += f"  -- {part.token}"
            rprint(output)

    if title_enabled:
        console.rule()
