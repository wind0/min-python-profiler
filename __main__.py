import time
import sys
from timer import profile


@profile
def foo(n):
    print('>>> foo')
    bar(n / 4)
    bar(n / 2)
    baz()
    time.sleep(n)


def bar(n):
    print('>>> bar')
    time.sleep(n)
    barsub()
    barsub()


def baz():
    print('>>> baz')
    time.sleep(0.050)

def barsub():
    print('>>>>>> barsub')
    time.sleep(0.1)
    

if __name__ == "__main__":
    foo(1)
