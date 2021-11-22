"""
Lexers
======

Additional Lexers not included in Pygments

"""
import re

from pygments.lexer import Lexer, do_insertions
from pygments.lexers import BashLexer
from pygments.token import Comment, Generic, Text

# =============================================================================

line_re = re.compile('.*?\n')

# =============================================================================

class DollarBashSessionLexer(Lexer):
    """Changes behaviour of the BashSessionLexer to assume a prompt uses a '$'.
    This allows the use of inline comments as it disallows '#' as a prompt and
    better handles virtual-env style prompts with lots of stuff left of the
    '$'.
    """
    _innerLexerCls = BashLexer
    _ps1rgx = re.compile(r'^([^$]*[$]\s)(.*\n?)')
    _ps2 = '> '

    _venv = re.compile(r'^(\([^)]*\))(\s*)')

    def get_tokens_unprocessed(self, text):
        innerlexer = self._innerLexerCls(**self.options)

        pos = 0
        curcode = ''
        insertions = []
        backslash_continuation = False

        for match in line_re.finditer(text):
            line = match.group()

            venv_match = self._venv.match(line)
            if venv_match:
                venv = venv_match.group(1)
                venv_whitespace = venv_match.group(2)
                insertions.append((len(curcode),
                    [(0, Generic.Prompt.VirtualEnv, venv)]))
                if venv_whitespace:
                    insertions.append((len(curcode),
                        [(0, Text, venv_whitespace)]))
                line = line[venv_match.end():]

            m = self._ps1rgx.match(line)
            if m:
                # To support output lexers (say diff output), the output
                # needs to be broken by prompts whenever the output lexer
                # changes.
                if not insertions:
                    pos = match.start()

                insertions.append((len(curcode),
                                   [(0, Generic.Prompt, m.group(1))]))
                curcode += m.group(2)
                backslash_continuation = curcode.endswith('\\\n')
            elif backslash_continuation:
                if line.startswith(self._ps2):
                    insertions.append((len(curcode),
                                    [(0, Generic.Prompt, line[:len(self._ps2)])]))
                    curcode += line[len(self._ps2):]
                else:
                    curcode += line
                backslash_continuation = curcode.endswith('\\\n')
            else:
                if insertions:
                    toks = innerlexer.get_tokens_unprocessed(curcode)
                    for i, t, v in do_insertions(insertions, toks):
                        yield pos+i, t, v
                if line[0] == '#':
                    yield match.start(), Comment, line
                else:
                    yield match.start(), Generic.Output, line

                insertions = []
                curcode = ''
        if insertions:
            for i, t, v in do_insertions(insertions,
                                         innerlexer.get_tokens_unprocessed(curcode)):
                yield pos+i, t, v
