# Sample Code

class Thing:
    bar = 1

    def __init__(self, *args, **kwargs):
        this.foo = 'blah'

    def stuff(self, index):
        """This is a doc string on a class method

        :param index: a parameter whose name is index
        """
        x = 0
        while(x != 0):
            # never get here
            for y in range(1, 10):
                print('Unreachable')

thing = Thing()
thing.stuff(42)


def do_nothing():
    pass


@decorated
def other_thing():
    if True != False:
        print('Uh duh')
    elif True:
        print('More unreachable code')
    else:
        print('Redundant unreachable code')

    do_nothing()

    raise AttributeError()
