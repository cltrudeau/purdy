#!/usr/bin/env python

from purdy.content import Code

print('****** Original')
code = Code('../display_code/doubles.py')
print(code.source)

print('\n****** Remove double with trim')
code = Code('../display_code/doubles.py')
code.remove_double_blanks()
print(code.source)


print('\n****** Remove double with trim, respect whitespace')
code = Code('../display_code/doubles.py')
code.remove_double_blanks(False)
print(code.source)

print('\n****** Remove line 5')
code = Code('../display_code/doubles.py')
code.remove_lines(5)
print(code.source)


print('\n****** Remove line 7-9')
code = Code('../display_code/doubles.py')
code.remove_lines(7, 2)
print(code.source)


print('\n****** Replace line 5')
code = Code('../display_code/doubles.py')
code.replace_line(5, 'def new_content():')
print(code.source)


print('\n****** Inline replace line 5')
code = Code('../display_code/doubles.py')
code.inline_replace(5, 5, 'inline_replaced():')
print(code.source)


print('\n****** Insert')
code = Code('../display_code/doubles.py')
code.insert_line(1, '# this is a new comment')
print(code.source)


print('\n****** Python partial')
code = Code('../display_code/doubles.py')
code.python_portion('foo')
print(code.source)


print('\n****** Left justify NOP')
code = Code(text="""\
def foo():
    pass
""")
code.left_justify()
print(code.source)


print('\n****** Left justify')
code = Code(text="""\
    def foo():
        pass
""")
code.left_justify()
print(code.source)
