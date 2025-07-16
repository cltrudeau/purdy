# _debug.py
# Debug Utilities

# To exclude the whole file from coverage reporting (it is only debug utils),
# put a pragma on a branch containing the whole file; hanky but it works
if True: # pragma: no cover
    from rich.console import Console

    # =======================================================================

    console = Console(highlight=False)
    rprint = console.print

    # =======================================================================
    # Print Debug Info
    # =======================================================================

    def print_cr(text, title=""):
        output = text.replace("\n", "↩️\n")
        console.rule(title)
        rprint(output, style="reverse")
        console.rule()


    def print_plain_output(code, title=""):
        # Prints output from the plain.TextCode
        console.rule(title)
        for line in code:
            if line is None:
                rprint(None, style="bold")
            else:
                rprint("[reverse]" + line + "[/reverse]", end='')

        console.rule()


    def print_code_lines(lines, title=""):
        console.rule(title)
        for line in lines:
            rprint( (f"CodeLine({line.spec.lexer_cls.__name__}, "
                f"{line.has_newline}") )
            for part in line.parts:
                rprint(f"   [reverse]{part.text}[/]  -- {part.token}")

        console.rule()


    def print_code_parts(parts, title=""):
        console.rule(title)
        for part in parts:
            rprint(f"   [reverse]{part.text}[/]  -- {part.token}")

        console.rule()


    def compare_code_lines(lines, compare=None, title=""):
        console.rule(title)
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
