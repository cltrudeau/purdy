from unittest import TestCase

from pygments.token import Token

from purdy.parser import (PurdyLexer, BlankCodeLine, CodeLine, CodePart, 
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
        names = list(PurdyLexer.names())
        self.assertEqual(5, len(names))
        names = set(names)

        expected = set(['py3', 'con', 'bash', 'dbash', 'node'])
        self.assertEqual(expected, names)

        #--- Test the choices property
        choices = PurdyLexer.choices().split(',')
        self.assertEqual(5, len(choices))

        self.assertIn('"py3" (Python 3 Source)', PurdyLexer.choices())
        self.assertIn('"con" (Python 3 Console)', PurdyLexer.choices())
        self.assertIn('"bash" (Bash Console)', PurdyLexer.choices())
        self.assertIn('"dbash" (Bash Console with a dollar', PurdyLexer.choices())
        self.assertIn('"node" (JavaScript Node.js Console)', 
            PurdyLexer.choices())

        #--- Test lexer detection
        lexer = PurdyLexer.factory_from_source(PYCON_SOURCE)
        self.assertEqual('con', lexer.name)

        lexer = PurdyLexer.factory_from_source(PY_SCRIPT)
        self.assertEqual('py3', lexer.name)

        lexer = PurdyLexer.factory_from_source(BASHCON_SOURCE)
        self.assertEqual('bash', lexer.name)

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

        lexer = PurdyLexer.factory_from_name('py3')
        line = CodeLine([CodePart(Token.Text, 'foo'), ], lexer, line_number=10)

        expected = 'CodeLine(" 10 foo")'
        self.assertEqual(expected, line.__repr__())
