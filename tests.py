from functools import wraps

def caller(func):
    return func()

def y (func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(test='Hello world!')

    return wrapper

def x (func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(kwargs)
        return func(*args, **kwargs)

    return y(wrapper)

@caller
@x
def z (*, test):
    print(test)
    print('Z called')
