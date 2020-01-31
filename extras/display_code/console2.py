>>> # This is a comment
>>> numbers = [6, 3, 9, 1]
>>> 
>>> sorted(numbers)
[1, 3, 6, 9]
>>> numbers
[6, 3, 9, 1]
>>> None < "3"
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: '<' not supported between instances of 'NoneType' and 'str'
>>> for x in [1, 2, 3]
  File "<stdin>", line 1
    for x in [1, 2, 3]
                     ^
SyntaxError: invalid syntax
>>> for x in [1, 2, 3]:
...     print(x)
... 
1
2
3
>>> def foo(a, b):
...     pass
... 
>>> class Foo(object):
...     BAR = 12
...
...     def bar(self):
...             pass
>>> @decorated
... def thing(a, b, c):
...     numbers = [1, 2, 3, 0.2, 0x12]
...     x = sorted(numbers)
... 
...     raise AttributeError('string' + "string")
... 
...     for x in range(1, 10):
...         while(True):
...             try:
...                b = numbers[0]
...             except IndexError:
...                break
... 
