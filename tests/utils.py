# tests/utils.py

from purdy.parser import CodeLine

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
    print("****")
    print(output)
    print("****")


def print_plain_output(code):
    # Prints output from the plain.TextCode
    print("****")
    for line in code:
        if line is None:
            print(None)
        else:
            print("➡️", line, "⬅️", end='')
    print("****")


def print_code_lines(lines):
    print("****")
    for line in lines:
        print(f"CodeLine({line.spec.lexer_cls.__name__}, {line.has_newline}")
        for part in line.parts:
            print(f"   ➡️{part.text}⬅️  -- {part.token}")
    print("****")


def compare_code_lines(self, lines, compare=None):
    for index, line in enumerate(lines):
        print("---------")
        if compare:
            try:
                for part in compare[index].parts:
                    print(f"   ➡️{part.text}⬅️  -- {part.token}")
                print(">>>")
            except IndexError:
                print("!!!!! Size mismatch, only printing lines now")
                compare = False

        for part in line.parts:
            print(f"   ➡️{part.text}⬅️  -- {part.token}")
