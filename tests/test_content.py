from unittest import TestCase
from unittest.mock import patch, mock_open

from pygments.token import Token
from waelstow import capture_stdout

from purdy.content import Code, CodePart, CodeLine

# =============================================================================

PY_CODE_LINES = [
    CodeLine([
        CodePart(Token.Comment.Single, '# Sample Code'),
    ]),
    CodeLine([
        CodePart(Token.Text, ''),
    ]),
    CodeLine([
        CodePart(Token.Keyword, 'def'),
        CodePart(Token.Text, ' '),
        CodePart(Token.Name.Function, 'foo'),
        CodePart(Token.Punctuation, '('),
        CodePart(Token.Punctuation, ')'),
        CodePart(Token.Punctuation, ':'),
    ]),
    CodeLine([
        CodePart(Token.Text, '    '),
        CodePart(Token.Literal.String.Doc, '"""Multi-line'),
    ]),
    CodeLine([
        CodePart(Token.Literal.String.Doc, '    Doc string'),
    ]),
    CodeLine([
        CodePart(Token.Literal.String.Doc, '    """'),
    ]),
    CodeLine([
        CodePart(Token.Text, '    '),
        CodePart(Token.Name, 'bar'),
        CodePart(Token.Text, ' '),
        CodePart(Token.Operator, '='),
        CodePart(Token.Text, ' '),
        CodePart(Token.Literal.String.Single, "'"),
        CodePart(Token.Literal.String.Single, 'Thing'),
        CodePart(Token.Literal.String.Single, "'"),
    ]),
]

BASH_CODE_LINES = [
    CodeLine([
        CodePart(Token.Generic.Prompt, '$'),
        CodePart(Token.Text, ' '),
        CodePart(Token.Name.Builtin, 'echo'),
        CodePart(Token.Text, ' '),
        CodePart(Token.Literal.String.Double, '"hello\\nthere"'),
    ]),
    CodeLine([
        CodePart(Token.Generic.Output, 'hello'),
    ]),
    CodeLine([
        CodePart(Token.Generic.Output, 'there'),
    ]),
    CodeLine([
        CodePart(Token.Generic.Prompt, '$'),
        CodePart(Token.Text, ' '),
    ]),
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

class TestContent(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.py_source = data_lines_to_source(PY_CODE_LINES)
        cls.bash_source = data_lines_to_source(BASH_CODE_LINES)

    def assert_code_parts(self, line_list, code):
        # loop through line_list (consists of manually created CodeLine
        # objects) and compare it to the actually parsed code object
        for i, line in enumerate(code.lines):
            for j, part in enumerate(line.parts):
                expected = line_list[i].parts[j]

                #print(part.token, '=>', part.text)
                #continue

                try:
                    self.assertEqual(expected.token, part.token)
                    self.assertEqual(expected.text, part.text)
                except AssertionError as e:
                    raise AssertionError(str(e) + f' CodeLine[{i}]')
                
    def test_content(self):
        global PY_CODE_LINES, BASH_CODE_LINES

        # need to test both py3 and bash to get all parsing cases
        code = Code('py3', content=self.py_source)
        self.assert_code_parts(PY_CODE_LINES, code)

        with patch('builtins.open', mock_open(read_data=self.bash_source)):
            code = Code('bash', content_filename='foo')
            self.assert_code_parts(BASH_CODE_LINES, code)

        # test line numbering
        code.reset_line_numbers(3)
        for index, line in enumerate(code.lines):
            self.assertEqual(index + 3, line.line_number)

        code.remove_line_numbers()
        for line in code.lines:
            self.assertEqual(-1, line.line_number)
