#!/usr/bin/env python
# preproc.py
#
# Demonstrates src code manipulation routines
from purdy.content import PyText

SRC = """\
# Header comment
def print_name(name):
    # This function prints out a name
    print(name)


class Car:
    def drive(self):
        # This method pretends to drive
        print("Vrooom")
"""


original = PyText.text(SRC)

print(80*"=")
print("Just the 'print_name' function")
part = original.get_part("print_name")
print(55*"-")
print(part)

print(80*"=")
print("The 'Car' class with the file's first line")
part = original.get_part("Car", header=1)
print(55*"-")
print(part)

print(80*"=")
print("The 'drive' method, left justified")
part = original.get_part("Car.drive")
part = part.left_justify()
print(55*"-")
print(part)

print(80*"=")
print("Double blank lines removed")
part = original.remove_double_blanks()
print(55*"-")
print(part)
