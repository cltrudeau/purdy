# Sample Code
def do_nothing():
    pass

class Thing:
    bar = 1

    def __init__(self, *args, **kwargs):
        this.foo = 'blah'

    @classmethod
    def stuff(cls, index):
        """This is a doc string on a class method that has a lot to say in fact so much so that it wraps the line. Twice even, it just goes on forever.

        :param index: a parameter whose name is index
        """
        x = 0
        while(x != 0):
            # never get here
            for y in range(1, 10):
                print('Unreachable')

        if True != False:
            print('Uh duh', [1, 2, 3])
        elif x < 10:
            print('More unreachable code', ("a", "b") )
        else:
            print('Redundant unreachable code', {"x": "y"} )

        do_nothing()
        raise AttributeError()

thing = Thing()
thing.stuff(42)

# Again
def do_nothing():
    pass

class Thing:
    bar = 1

    def __init__(self, *args, **kwargs):
        this.foo = 'blah'

    @classmethod
    def stuff(cls, index):
        """This is a doc string on a class method that has a lot to say in fact so much so that it wraps the line. Twice even, it just goes on forever.

        :param index: a parameter whose name is index
        """
        x = 0
        while(x != 0):
            # never get here
            for y in range(1, 10):
                print('Unreachable')

        if True != False:
            print('Uh duh', [1, 2, 3])
        elif x < 10:
            print('More unreachable code', ("a", "b") )
        else:
            print('Redundant unreachable code', {"x": "y"} )

        do_nothing()
        raise AttributeError()

thing = Thing()
thing.stuff(42)
