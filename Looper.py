#!/usr/bin/env python
#-*- encoding: gb2312 -*-


"""
Looper is a loop timer that runs the given `func` each `interval` seconds.
It is inspired by threading.Timer().
"""

import threading


class Looper(threading.Thread):
    def __init__(self, interval, func, args=[], kwargs={}):
        threading.Thread.__init__(self)
        self._interval = float(interval)
        self._func = func
        self._args = tuple(args)
        self._kwargs = dict(kwargs)
        self._finished = threading.Event()

    def terminate(self):
        self._finished.set()

    def run(self):
        while not self._finished.isSet():
            self._finished.wait(self._interval)
            if self._finished.isSet():
                break
            self._func(*self._args, **self._kwargs)


if __name__ == '__main__':
    import time
    def func():
        print 1

    loop = Looper(0.1, func, [], {})
    loop.start()
    time.sleep(1)
    print 'terminate'
    loop.terminate()
