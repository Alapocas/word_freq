from wordc_api import test
import time

if __name__ == '__main__':
    t1 = time.time()
    test()
    t2 = time.time()
    print(t2-t1)