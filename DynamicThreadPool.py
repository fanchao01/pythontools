#!/usr/bin/env python
#-*- encoding:utf-8 -*-
"""
DynamicThreadPool is a pool of dynamic non-joinable threads.
e.g.
    def func(i):
        print i

    pool = DynamicThreadPool(2, 10)
    for i in range(100):
        pool.post_task(func, i)

    pool.terminate()

`max_worker_threads` threads to work, and each one keep alive `max_idle_before_exit` seconds at least.
post_task() method will add a task, and run it as soon as possible.
terminate() method will exit all threads at idle, but busy threads will run to end.

TODO:
`max_capacity` is planned to limit the max tasks to put at the same time.

Known:
Python does not surpport the multi-thread concept as the pthread library in linux,
all threads work only in one Process. :<)
"""
import os
import time
import logging

from collections import deque
from threading import Thread
from threading import RLock as Mutex   
from threading import Condition as ConVar


class Empty(Exception):
    """Queue Empty Exception"""


class Full(Exception):
    """Queue Full Exception"""


class Queue(object):
    def __init__(self, max_capacity=0):
        self._max_capacity = max_capacity
        self._size = 0
        self._queue = deque()

    def pop(self):
        if not self._size:
            raise Empty
        self._size -= 1
        return self._queue.pop()

    def put(self, item):
        if self._max_capacity and self._size >= self._max_capacity:
            raise Full
        self._queue.appendleft(item)
        self._size += 1
        return self._size

    def empty(self):
        return not self._size

    def size(self):
        return self._size

    def capacity(self):
        return self.max_capacity


class PendingTask(object):
    """A task with a function, which the threads will work on"""
    def __init__(self, func=None, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.func(*self.args, **self.kwargs)

    def is_close_down(self):
        """
        The thread received the task will quit, 
        if the task's func is None
        """
        return self.func is None


class Worker(Thread):
    def __init__(self, pool):
        super(Worker, self).__init__()
        self.pool = pool

        self.daemon = True

    @staticmethod
    def spawn_daemonic_thread(pool):
        worker = Worker(pool)
        worker.start()
        return worker

    def run(self):
        logging.debug("[{0}] thread starts".format(self.ident))

        while True:
            task = self.pool.wait_task()
            if task.is_close_down():
                break
            task()

        self.pool.desc_spawned_thread()
        logging.debug("[{0}] thread ends".format(self.ident))


class DynamicThreadPool(object):
    def __init__(self, max_worker_threads, max_idle_before_exit, max_capacity=0):
        self.max_worker_threads = max_worker_threads
        self.max_idle_before_exit = max_idle_before_exit
        self.terminated = False

        self.mutex = Mutex()
        self.n_idle_threads = 0
        self.n_spawned_threads = 0

        self.pending_queue = Queue(max_capacity)
        self.pending_queue_convar = ConVar(self.mutex)

    def post_task(self, func, *args, **kwargs):
        logging.debug("post task, func: {0} args: {1}, kwargs: {2}"
                      .format(func, args, kwargs))
        return self._post_task(PendingTask(func, *args, **kwargs))

    def _post_task(self, task):
        assert self.n_spawned_threads >= 0

        with self.mutex as lock:
            self.pending_queue.put(task)
            if (self.n_idle_threads < self.pending_queue.size()
                    and self.n_spawned_threads < self.max_worker_threads):
                Worker.spawn_daemonic_thread(self)
                self.n_spawned_threads += 1
            else:
                self.pending_queue_convar.notify()
        return True

    def wait_task(self):
        with self.mutex as lock:
            left_time = self.max_idle_before_exit
            end_time = time.time() + left_time
            while self.pending_queue.empty() and left_time > 0 and not self.terminated:
                self.n_idle_threads += 1
                self.pending_queue_convar.wait(left_time)
                self.n_idle_threads -= 1
                left_time = end_time - time.time()

            try:
                task = self.pending_queue.pop()
            except Empty:
                return PendingTask()
            else:
                return task

    def terminate(self):
        with self.mutex as lock:
            if self.terminated:
                return
            self.terminated = True
            self.pending_queue_convar.notifyAll()

    def desc_spawned_thread(self):
        with self.mutex as lock:
            self.n_spawned_threads -= 1


if __name__ == "__main__":
    import random


    def func(*args, **kwargs):
        print '[{0}] starts job'.format(args[0])
        time.sleep(random.randint(1, 3)/10.0)
        print '[{0}] ends job'.format(args[0])

    pool = DynamicThreadPool(4, 10)
    for i in range(10):
        pool.post_task(func, ('seq %d' % i, i), {'k':i})

    time.sleep(1)
    pool.post_task(func, ('last work', 'last'), {'last':'last'})

    pool.terminate()
    #leave time for the pool existed, before all global varibles become None
    time.sleep(0.5)

