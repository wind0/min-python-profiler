import time
import sys
from timer import Profiler



def testfunc(num):
    time.sleep(1)
    print(f"{num}")

def main():
    profiler = Profiler()
    sys.setprofile(profiler._profiler)
    for i in range(10): 
        testfunc(i)
    sys.setprofile(None)
    profiler.profiling_results_printing()

if __name__ == "__main__":
    main()
