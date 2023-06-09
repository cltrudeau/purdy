class Cat:
    def __init__(self, name):
        self.name = name

    def meow(self):
        print(f"Meow, {self.name}")


def dog(woof):
    print("Woof, woof")
    print(woof)


def snake(slither):
    slither = slither + 5
    return slither
