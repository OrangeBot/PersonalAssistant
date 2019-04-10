class Test(object):
    def __init__(self):
        self.kektest = 'kektest'

    def testm(self):
        print("test")
        return "Test_result"


if __name__ == '__main__':
    t = Test()
    print("testm is a method")
    print(type(t.testm))
    print(callable(t.testm))

    print("kektest is a method")
    print(type(t.kektest))
    print(callable(t.kektest))
