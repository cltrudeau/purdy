#! /usr/bin/env python

class Code:
    def __init__(self):
        self._current = 0
        self._lines = [1, 3, 5, 7, 9]

    def _iterate(self, start, end):
        for index in range(start, end):
            yield self._lines[index]

    def __iter__(self):
        return self._iterate(0, len(self._lines))

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._iterate(index.start, index.stop)
        else:
            return self._lines[index]

    def chunk(self, amount):
        start = self._current
        end = start + amount
        self._current = end
        if end > len(self._lines):
            end = len(self._lines)

        return self._iterate(start, end)


code = Code()
for item in code:
    print(f'iter:{item}')


print(f'piece:{code[2]}')

for item in code[1:3]:
    print(f'sliced:{item}')


for item in code.chunk(2):
    print(f'chunk1:{item}')

for item in code.chunk(2):
    print(f'chunk2:{item}')

for item in code.chunk(5):
    print(f'chunk3:{item}')

for item in code.chunk(1):
    print(f'chunk4:{item}')
