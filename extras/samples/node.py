#!/usr/bin/env python

### Example purdy library code
#
# Demonstrates the use of a custom lexer

from purdy.actions import Append, Wait, AppendTypewriter
from purdy.content import Code
from purdy.parser import PurdyLexer
from purdy.ui import SimpleScreen

from pygments.lexers.javascript import JavascriptLexer

screen = SimpleScreen()
code_box = screen.code_box

text = """// JavaScript Code
let a = 3
let b = '4'
if(a) {
  console.log(a)
}

// ===============================
"""

lexer = PurdyLexer('js', 'Javascript', JavascriptLexer, False, 'code')
js = Code(text=text, lexer_name='custom', purdy_lexer=lexer)

text = """
// Node.js Console Session
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
> b === a
false
> if(a) {
...   console.log(a)
... }
3
undefined
> c
Uncaught ReferenceError: c is not defined
"""

node = Code(text=text, lexer_name='node')


actions = [
    Append(code_box, js),
    Wait(),
    AppendTypewriter(code_box, node),
]

if __name__ == '__main__':
    screen.run(actions)
