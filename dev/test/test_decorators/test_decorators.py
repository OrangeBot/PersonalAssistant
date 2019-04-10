# what i want here?
# to create a prototype of a decorator
# to use with schedulable tasks of PA
# the decorator should register method

# todo: how do i create a class-specific decorator?
# oh, decorator will get self

# IMPORTANT:
# so, you can't pass a class instance to decorator
# but i can do this via metaclasses - process decorated methods upon class creation. And it's actually neat
import six


def decorator_factory(repeated=True):
    def custom_decorator(func):
        def new_func(*args, **kwargs):
            print("custom decorator activated")
            return func(*args, **kwargs)

        new_func.flag = None
        new_func.repeated = repeated
        return new_func

    return custom_decorator


class TestMeta(type):
    def __init__(cls, name, bases, dct):
        super(TestMeta, cls).__init__(name, bases, dct)

        cls._schedulable_tasks = {}
        # for k, v in dct
        print(type(dct))
        for k, v in six.iteritems(dct):
            if hasattr(v, 'flag'):  # decorated methods
                cls._schedulable_tasks[k] = v
                print("Detected decorated method '{}'".format(k))
        # cls.class_name = to_snake_case(name)


class Test(object):
    __metaclass__ = TestMeta

    @decorator_factory(repeated=False)
    def test_decorated_method(self):
        print("Decorated function launched")


if __name__ == '__main__':
    t = Test()
    t.test_decorated_method()
