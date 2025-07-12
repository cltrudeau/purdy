from pathlib import Path
from unittest import TestCase

from pygments.lexers import PythonConsoleLexer
from pygments.token import Token

from purdy.parser import (CodeLine, CodePart, LexerSpec, Parser, PartsList,
    token_is_a, token_ancestor)

from utils import code_liner

# =============================================================================

class TestTokenComparison(TestCase):
    def test_token_is_a(self):
        # Same token case
        self.assertTrue( token_is_a(Token.Keyword, Token.Keyword) )

        # Parent token case
        self.assertTrue( token_is_a(Token.Text.Whitespace, Token.Text) )

        # Not equal case
        self.assertFalse( token_is_a(Token.Text, Token.Keyword) )

    def test_ancestor(self):
        # Perfect match case
        result = token_ancestor(Token.Text, [Token.Text])
        self.assertEqual(Token.Text, result)

        # Ancestor case
        result = token_ancestor(Token.Text.Whitespace, [Token.Text])
        self.assertEqual(Token.Text, result)

        # Default case
        result = token_ancestor(Token.Text.Whitespace, [Token.Keyword])
        self.assertEqual(Token, result)


class TestLexerSpec(TestCase):
    def test_find(self):
        # Test straight look-up
        spec = LexerSpec.find("repl")
        self.assertEqual(LexerSpec.built_ins["repl"], spec)

        # Test alias
        spec = LexerSpec.find("txt")
        self.assertEqual(LexerSpec.built_ins["plain"], spec)

        # Test name listing
        expected = len(LexerSpec.built_ins) + len(LexerSpec.aliases)
        count = len(LexerSpec.names)
        self.assertEqual(expected, count)

        for name in LexerSpec.built_ins.keys():
            self.assertIn(name, LexerSpec.names)

        for name in LexerSpec.aliases.keys():
            self.assertIn(name, LexerSpec.names)

        # Test bad choice
        with self.assertRaises(ValueError):
            LexerSpec.find("not_a_lexer_name")


class TestPartsList(TestCase):
    def test_partslist(self):
        parts = PartsList()
        self.assertEqual(0, parts.text_length)

        parts.append(CodePart(Token.Keyword, 'def'))
        self.assertEqual(3, parts.text_length)

        parts[0] = CodePart(Token.Keyword, 'if')
        self.assertEqual(2, parts.text_length)

        parts.insert(0, CodePart(Token.Keyword, 'def'))
        self.assertEqual(5, parts.text_length)

        del parts[1]
        self.assertEqual(3, parts.text_length)

        second = PartsList()
        second.append(CodePart(Token.Keyword, 'else'))

        parts.extend(second)
        self.assertEqual(7, parts.text_length)

        self.assertEqual("defelse", parts.all_text)


class TestCodeLine(TestCase):
    def test_codeline(self):
        plain = LexerSpec.built_ins["plain"]
        repl = LexerSpec.built_ins["repl"]

        # Check the repr doesn't blow up (read: get my coverage count up)
        line = CodeLine(plain)
        repr(line)

        # Validate error handling
        #
        # Trigger __eq__
        self.assertTrue(plain == plain)

        # Equality test: classes
        self.assertFalse(line == CodeLine(repl))

        # Equality test: newline marker
        line.has_newline = True
        self.assertFalse(line == CodeLine(plain))
        line.has_newline = False

        # Equality test: parts count
        line.parts.append(CodePart(Token.Keyword, 'def'))
        self.assertFalse(line == CodeLine(plain))

        # Equality test: equal part count but different contents
        line2 = code_liner(plain, False, CodePart(Token.Keyword, 'if'))
        self.assertFalse(line == line2)


class TestParser(TestCase):
    def test_constructor(self):
        # Auto detect case
        expected = LexerSpec.built_ins["py"]
        parser = Parser("detect", hint="data/simple.py")
        self.assertEqual(expected, parser.spec)

        # Named case
        expected = LexerSpec.built_ins["py"]
        parser = Parser("py")
        self.assertEqual(expected, parser.spec)

        # LexerSpec case
        expected = LexerSpec.built_ins["py"]
        parser = Parser(expected)
        self.assertEqual(expected, parser.spec)

        # Pygments Lexer Case
        parser = Parser(PythonConsoleLexer)
        self.assertEqual("custom_PythonConsoleLexer", parser.spec.description)
        self.assertEqual(PythonConsoleLexer, parser.spec.lexer_cls)

        # Error handling: deal with class that isn't a Pygments Lexer, any old
        # class will do as long as it isn't a useful one
        with self.assertRaises(ValueError):
            Parser(TestCase)

    def test_newline_handling(self):
        parser = Parser("py")

        # With newline
        content = "x=1\n"
        result = parser.parse(content)
        self.assertEqual(1, len(result))
        self.assertTrue(result[0].has_newline)

        # Without newline
        content = "x=1"
        result = parser.parse(content)
        self.assertEqual(1, len(result))
        self.assertFalse(result[0].has_newline)

    def test_simple(self):
        parser = Parser("py")

        path = (Path(__file__).parent / Path("data/simple.py")).resolve()
        content = path.read_text()

        expected = [
            code_liner(parser.spec, True,
                CodePart(Token.Comment.Single,
                    '# Small file for simple parser testing')
            ),
            code_liner(parser.spec, True,
                CodePart(Token.Keyword, 'def'),
                CodePart(Token.Text.Whitespace, ' '),
                CodePart(Token.Name.Function, 'simple'),
                CodePart(Token.Punctuation, '('),
                CodePart(Token.Name, 'thing'),
                CodePart(Token.Punctuation, ')'),
                CodePart(Token.Punctuation, ':')
            ),
            code_liner(parser.spec, True,
                CodePart(token=Token.Text.Whitespace, text='    '),
                CodePart(token=Token.Literal.String.Doc,
                    text='"""This tests')
            ),
            code_liner(parser.spec, True,
                CodePart(token=Token.Literal.String.Doc,
                    text='    multi-line strings"""')
            ),
            code_liner(parser.spec, True,
                CodePart(token=Token.Text, text='    '),
                CodePart(token=Token.Keyword, text='return'),
                CodePart(token=Token.Text, text=' '),
                CodePart(token=Token.Name, text='thing'),
                CodePart(token=Token.Text, text=' '),
                CodePart(token=Token.Operator, text='+'),
                CodePart(token=Token.Text, text=' '),
                CodePart(token=Token.Literal.String.Double, text='"'),
                CodePart(token=Token.Literal.String.Escape, text='\\n'),
                CodePart(token=Token.Literal.String.Double, text='Done'),
                CodePart(token=Token.Literal.String.Double, text='"')
            ),
            code_liner(parser.spec, True, CodePart(Token.Text.Whitespace, '')),
            code_liner(parser.spec, True,
                CodePart(token=Token.Name, text='simple'),
                CodePart(token=Token.Punctuation, text='('),
                CodePart(token=Token.Literal.String.Double, text='"'),
                CodePart(token=Token.Literal.String.Double, text='A string'),
                CodePart(token=Token.Literal.String.Escape, text='\\n'),
                CodePart(token=Token.Literal.String.Double,
                    text='With newline'),
                CodePart(token=Token.Literal.String.Double, text='"'),
                CodePart(token=Token.Punctuation, text=')')
            ),
        ]

        lines = parser.parse(content)
        self.assertEqual(expected, lines)

    def test_blank_lines(self):
        parser = Parser("py")

        content = "   \n\nx=1\n"
        expected = [
            code_liner(parser.spec, True,
                CodePart(token=Token.Text, text='   ')
            ),
            code_liner(parser.spec, True,
                CodePart(token=Token.Text.Whitespace, text='')
            ),
            code_liner(parser.spec, True,
                CodePart(token=Token.Name, text='x'),
                CodePart(token=Token.Operator, text='='),
                CodePart(token=Token.Literal.Number.Integer, text='1')
            ),
        ]

        lines = parser.parse(content)
        self.assertEqual(expected, lines)

    def test_multiline_output(self):
        parser = Parser("con")

        path = (Path(__file__).parent / Path("data/curl.con")).resolve()
        content = path.read_text()

        expected = [
            code_liner(parser.spec, True,
                CodePart(token=Token.Generic.Output, text='')
            ),
            code_liner(parser.spec, True,
                CodePart(token=Token.Generic.Prompt, text='$ '),
                CodePart(token=Token.Text, text='curl'),
                CodePart(token=Token.Text.Whitespace, text=' '),
                CodePart(token=Token.Text, text='--include'),
                CodePart(token=Token.Text.Whitespace, text=' '),
                CodePart(token=Token.Text,
                    text='http://127.0.0.1:8000/redirect/')
            ),
            code_liner(parser.spec, True,
                CodePart(token=Token.Generic.Output,
                    text='HTTP/1.1 302 Found')
            ),
            code_liner(parser.spec, True,
                CodePart(token=Token.Generic.Output,
                    text='Date: Tue, 21 Apr 2020 19:31:07 GMT')
            ),
        ]

        lines = parser.parse(content)
        self.assertEqual(expected, lines)

    def test_after_newline(self):
        # Some lexers aren't line oriented so you can end up with stuff after
        # a \n character
        content = "<html>\n     <!-- comment -->"
        parser = Parser("html")

        expected = [
            code_liner(parser.spec, True,
                CodePart(token=Token.Punctuation, text='<'),
                CodePart(token=Token.Name.Tag, text='html'),
                CodePart(token=Token.Punctuation, text='>')
            ),
            code_liner(parser.spec, False,
                CodePart(token=Token.Text, text='     '),
                CodePart(token=Token.Comment.Multiline,
                    text='<!-- comment -->')
            ),
        ]

        lines = parser.parse(content)
        self.assertEqual(expected, lines)

    def test_empty_token(self):
        # Some lexers spit out empty tokens, purdy should ignore them
        parser = Parser("repl")
        content = """Traceback (most recent call last):\n>>> """

        expected = [
            code_liner(parser.spec, True,
                CodePart(token=Token.Generic.Traceback,
                    text='Traceback (most recent call last):')
            ),
            code_liner(parser.spec, False,
                CodePart(token=Token.Generic.Prompt, text='>>> ')
            ),
        ]

        lines = parser.parse(content)
        self.assertEqual(expected, lines)

#    def test_foo(self):
#        # Test to experiment with original sample code pieces
#        path = Path("/Users/ctrudeau/s/purdy1/extras/display_code")
#
#        path = path / Path("console.repl")
#        parser = Parser("repl")
#
#        content = path.read_text()
#        lines = parser.parse(content)
#
