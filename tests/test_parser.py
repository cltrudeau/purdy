from unittest import TestCase

from pygments.token import Token

from purdy.parser import (LEXERS, BlankCodeLine, CodeLine, CodePart, 
    token_is_a, token_ancestor)

# =============================================================================

PYCON_SOURCE = """\
>>> x = 1
"""

PY_SCRIPT = """\
#!/usr/bin/env python

print('hello')
"""

BASHCON_SOURCE = """\
$ echo "hello"
hello
"""

class TestParser(TestCase):
    def test_lexer_container(self):
        #--- Test the names property
        names = list(LEXERS.names)
        self.assertEqual(3, len(names))
        names = set(names)

        expected = set(['py3', 'con', 'bash'])
        self.assertEqual(expected, names)

        #--- Test the choices property
        choices = LEXERS.choices.split(',')
        self.assertEqual(3, len(choices))

        self.assertIn('"py3" (Python 3)', LEXERS.choices)
        self.assertIn('"con" (Python Console)', LEXERS.choices)
        self.assertIn('"bash" (Bash Console)', LEXERS.choices)

        #--- Test is_console attributes
        lexer = LEXERS.get_lexer('con')
        self.assertTrue(LEXERS.is_lexer_console(lexer))

        lexer = LEXERS.get_lexer('py3')
        self.assertFalse(LEXERS.is_lexer_console(lexer))

        lexer = LEXERS.get_lexer('bash')
        self.assertTrue(LEXERS.is_lexer_console(lexer))

        #--- Test lexer detection
        lexer = LEXERS.detect_lexer(PYCON_SOURCE)
        expected = LEXERS.get_lexer('con')
        self.assertEqual(expected, lexer)

        lexer = LEXERS.detect_lexer(PY_SCRIPT)
        expected = LEXERS.get_lexer('py3')
        self.assertEqual(expected, lexer)

        lexer = LEXERS.detect_lexer(BASHCON_SOURCE)
        expected = LEXERS.get_lexer('bash')
        self.assertEqual(expected, lexer)

    def test_tokens(self):

        #--- Test token_is_a()
        self.assertTrue( token_is_a(Token, Token) )
        self.assertTrue( token_is_a(Token.Name.Function, Token.Name) )
        self.assertFalse( token_is_a(Token.Name.Function, Token.Keyword) )

        #--- Test token_ancestor()
        token = token_ancestor(Token.Name.Function, [Token.Name.Function])
        self.assertEqual(Token.Name.Function, token)

        token = token_ancestor(Token.Name.Function, [Token.Name])
        self.assertEqual(Token.Name, token)

        token = token_ancestor(Token.Text, [Token.Name])
        self.assertEqual(Token, token)

    def test_misc(self):
        blank = BlankCodeLine()
        self.assertEqual('', blank.render_line(None))

        lexer = LEXERS.get_lexer('py3')
        line = CodeLine([CodePart(Token.Text, 'foo'), ], lexer, line_number=10)

        expected = 'CodeLine(" 10 foo")'
        self.assertEqual(expected, line.__repr__())
