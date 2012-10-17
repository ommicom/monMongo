__author__ = 'Omic'
__version__ = '0.0.1'

import threading

class Timer(threading.Thread):
    def __init__(self, call_func, cycle):
        threading.Thread.__init__(self)
        self.__proc = threading.Event()
        self.__cycle = cycle
        self.__call_func = call_func

    def run(self):
        while True:
            if self.__proc.isSet():
                return
            self.__call_func()
            self.__proc.wait(self.__cycle)

    def stop(self):
        self.__proc.set()

