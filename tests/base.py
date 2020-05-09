from unittest import TestCase

from pygments.token import Token

from purdy.parser import CodePart, CodeLine, LEXERS

# =============================================================================

py3_lexer = LEXERS.get_lexer('py3')
bash_lexer = LEXERS.get_lexer('bash')

PY_CODE_LINES = [
    CodeLine([
        CodePart(Token.Comment.Single, '# Sample Code'),
    ], py3_lexer),
    CodeLine([
        CodePart(Token.Text, ''),
    ], py3_lexer),
    CodeLine([
        CodePart(Token.Keyword, 'def'),
        CodePart(Token.Text, ' '),
        CodePart(Token.Name.Function, 'foo'),
        CodePart(Token.Punctuation, '('),
        CodePart(Token.Punctuation, ')'),
        CodePart(Token.Punctuation, ':'),
    ], py3_lexer),
    CodeLine([
        CodePart(Token.Text, '    '),
        CodePart(Token.Literal.String.Doc, '"""Multi-line'),
    ], py3_lexer),
    CodeLine([
        CodePart(Token.Literal.String.Doc, '    Doc string'),
    ], py3_lexer),
    CodeLine([
        CodePart(Token.Literal.String.Doc, '    """'),
    ], py3_lexer),
    CodeLine([
        CodePart(Token.Text, '    '),
        CodePart(Token.Name, 'bar'),
        CodePart(Token.Text, ' '),
        CodePart(Token.Operator, '='),
        CodePart(Token.Text, ' '),
        CodePart(Token.Literal.String.Single, "'"),
        CodePart(Token.Literal.String.Single, 'Thing'),
        CodePart(Token.Literal.String.Single, "'"),
    ], py3_lexer),
]

BASH_CODE_LINES = [
    CodeLine([
        CodePart(Token.Generic.Prompt, '$'),
        CodePart(Token.Text, ' '),
        CodePart(Token.Name.Builtin, 'echo'),
        CodePart(Token.Text, ' '),
        CodePart(Token.Literal.String.Double, '"hello\\nthere"'),
    ], bash_lexer),
    CodeLine([
        CodePart(Token.Generic.Output, 'hello'),
    ], bash_lexer),
    CodeLine([
        CodePart(Token.Generic.Output, 'there'),
    ], bash_lexer),
    CodeLine([
        CodePart(Token.Generic.Prompt, '$'),
        CodePart(Token.Text, ' '),
    ], bash_lexer),
]

# =============================================================================

def data_lines_to_source(data):
    text = []
    for line in data:
        words = []
        for part in line.parts:
            words.append(part.text)

        text.append(''.join(words))

    return '\n'.join(text)

# =============================================================================

class PurdyContentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.py_source = data_lines_to_source(PY_CODE_LINES)
        cls.bash_source = data_lines_to_source(BASH_CODE_LINES)
