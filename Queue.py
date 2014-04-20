#!/bin/env python
#-*- encoding: utf-8 -*-

__author__ = "fanchao01"
__version__ = "0.0.1"

'''multi-thread queue likes Queue.queue'''


import threading as _threading
import time as _time


class Full(Exception):
    """Exception Full raised by Queue.put/put_nowait"""

class Empty(Exception):
    """Exception Empty raised by Queue.get/get_nowait"""


class Queue(object):
    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self.queue = []

        #one lock with three condition-waiting queue
        self.mutex = _threading.Lock() 
        self.not_full = _threading.Condition(self.mutex)
        self.not_empty = _threading.Condition(self.mutex)

        self.all_tasks_done = _threading.Condition(self.mutex)
        self.un_finished_tasks = 0
    
    def clear(self):
        with self.mutex as lock:
            self.queue = []
            self.not_full.notify_all()

    def task_done(self):
        with self.all_tasks_done as condition:
            unfinished = self.un_finished_tasks - 1
            if unfinished < 0:
                raise ValueError("task_done() called too many times")
            elif unfinished == 0:
                self.all_tasks_done.notify_all()
            self.un_finished_tasks = unfinished

    def join(self):
        with self.all_tasks_done as condition:
            while self.un_finished_tasks > 0:
                self.all_tasks_done.wait()
            
    def qsize(self):
        with self.mutex as lock:
            return self._qsize()

    def _qsize(self): #there must be a way to get the size of self.queue without lock
        return len(self.queue)

    def full(self):
        with self.mutex as lock:
            return self.qsize() >= self.maxsize if self.maxsize > 0 else False

    def empty(self):
        with self.mutex as lock:
            return self.qsize() <= 0

    def _put(self, ele):
        self.queue.append(ele)
        self.un_finished_tasks += 1

    def put(self, ele, block=True, timeout=None):
        with self.not_full as condition:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize: #can not use self.qssize(), which will relock the self.mutex leading to deadlock
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("timeout must be >0, given(%d)" % timeout)
                else:
                    end = _time.time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = end - _time.time()
                        if remaining < 0.0:
                            raise Full
                        self.not_full.wait(remaining)

            self._put(ele)
            self.not_empty.notify()

    def put_nowait(self, ele):
        self.put(ele, False)

    def _get(self):
        return self.queue.pop(0)

    def get(self, block=True, timeout=None):
        with self.not_empty as condition:
            if not block:
                if self._qsize() == 0:
                    raise Empty
            elif timeout is None:
                while self._qsize() == 0:
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("timeout must be > 0, given(%d)" % timeout)
            else:
                end = _time.time() + timeout
                while self._qsize() == 0:
                    remaining = end  - _time.time()
                    if remaining < 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            ele = self._get()
            self.not_full.notify()
            return  ele 

    def get_notwait(self):
        self.get(False)

if __name__ == "__main__":
    import random
    import time

    class Worker(_threading.Thread):
        def __init__(self, queue):
            super(Worker, self).__init__()
            self.queue = queue

        def run(self):
            time.sleep(random.randint(1, 5) / 10.0)
            print self.queue.get()

    q = Queue(10)
    for i in range(10):
        q.put(i)

    try:
        q.put(11, True, 1)
    except Full:
        pass

    try:
        q.put_nowait(11)
    except Full:
        pass

    for i in range(10):
        Worker(q).start()

    q.task_done()
    w = Worker(q)
    w.start()
    q.put(10)

