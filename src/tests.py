def myfun(thing):
    thing.other = 20
    print(thing)

class A:
    def __init__(self):
        self.thing = 10
        myfun(self)

a = A()
print(a.thing)
print(a.other)