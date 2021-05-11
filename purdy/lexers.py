"""
Lexers
======

Additional Lexers not included in Pygments

"""
import re

from pygments.lexer import Lexer, do_insertions
from pygments.lexers.javascript import JavascriptLexer
from pygments.token import Generic

# =============================================================================

line_re = re.compile('.*?\n')

# =============================================================================

class NodeConsoleLexer(Lexer):
    """
    For parsing JavaScript within an interactive Node.js shell, such as:

    .. sourcecode:: nodejs

        > let a = 3
        undefined
        > a
        3
        > let b = '4'
        undefined
        > b
        '4'
        > b == a
        false

    """
    name = 'JavaScript Node.js console session'
    aliases = ['nodejs']
    mimetypes = ['application/javascript', 'application/x-javascript',
                 'text/x-javascript', 'text/javascript']

    def get_tokens_unprocessed(self, text):
        jslexer = JavascriptLexer(**self.options)

        curcode = ''
        insertions = []

        for match in line_re.finditer(text):
            line = match.group()
            if line.startswith('> '):
                insertions.append((len(curcode), 
                    [(0, Generic.Prompt, line[:2])]))

                curcode += line[2:]
            elif line.startswith('... '):
                insertions.append((len(curcode), 
                    [(0, Generic.Prompt, line[:4])]))

                curcode += line[4:]
            else:
                if curcode:
                    yield from do_insertions(insertions, 
                        jslexer.get_tokens_unprocessed(curcode))

                    curcode = ''
                    insertions = []

                yield from do_insertions([], 
                    jslexer.get_tokens_unprocessed(line))
