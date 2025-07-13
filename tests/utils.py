# tests/utils.py
from rich.console import Console

from purdy.parser import CodeLine

# ===========================================================================

console = Console(highlight=False)
rprint = console.print

# ===========================================================================

def code_liner(spec, newline, *args):
    line = CodeLine(spec, has_newline=newline)
    for arg in args:
        line.parts.append(arg)

    return line

# ===========================================================================
# Print Debug Info
# ===========================================================================

def print_cr(text):
    output = text.replace("\n", "↩️\n")
    console.rule()
    rprint(output, style="reverse")
    console.rule()


def print_plain_output(code):
    # Prints output from the plain.TextCode
    console.rule()
    for line in code:
        if line is None:
            rprint(None, style="bold")
        else:
            rprint("[reverse]" + line + "[/reverse]", end='')

    console.rule()


def print_code_lines(lines):
    console.rule()
    for line in lines:
        rprint(f"CodeLine({line.spec.lexer_cls.__name__}, {line.has_newline}")
        for part in line.parts:
            rprint(f"   [reverse]{part.text}[/]  -- {part.token}")

    console.rule()


def compare_code_lines(lines, compare=None):
    console.rule()
    for index, line in enumerate(lines):
        if compare:
            try:
                console.rule(style="blue")
                for part in compare[index].parts:
                    rprint(f"   [reverse]{part.text}[/]  -- {part.token}")

            except IndexError:
                rprint("[bold red]" +
                    "!!!!! Size mismatch, only printing first arg now")
                compare = False

        for part in line.parts:
            rprint(f"   [reverse]{part.text}[/]  -- {part.token}")

    console.rule()
