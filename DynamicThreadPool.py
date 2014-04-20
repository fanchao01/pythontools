#!/usr/bin/env python
#-*- encoding:utf-8 -*-


"""
DynamicThreadPool is a pool of dynamic threads. It could create and destroy the worker thread dynamically.
e.g.
    pool = DynamicThreadPool(2, 10)
    for i in range(100):
        pool.addTask(func, *args, **kwargs)

    pool.terminate()

'max_worker_threads' threads to work, each one alive 'max_idle_before_exit' seconds at least.
addTask() function will add a task, and run it as soon as possible.
terminate() function will exit all threads at idle, but still-running threads will run to end

TODO:
'max_capacity' argument is not implemented. Do not set this.

Known:
Python does not surpport the multi-thread concept as the pthread library in linux,
all threads work only in one Process. :<)
"""

__author__ = "fanchao01"
__version__ = "1.0.0"

from threading import Thread
from threading import Lock as Mutex, Condition as ConVar


class Full(Exception):
    pass


class Empty(Exception):
    pass


class TaskQueue(object):
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.data = []

    def size(self):
        return len(self.data)

    def empty(self):
        return not self.data

    def full(self):
        return self.max_capacity and self.size() >= self.max_capacity

    def pop(self):
        try:
            return self.data.pop()
        except IndexError:
            raise Empty("task queue empty")

    def put(self, item):
        if self.full():
            raise Full("task queue full")
        return self.data.insert(0, item)

    def clear(self):
        self.data = []


class PendingTask(object):
    def __init__(self, func=None, args=(), kwargs={}):
        self.args = tuple(args)
        self.kwargs = dict(kwargs)
        self.func = func

    def __call__(self):
        return self.func(*self.args, **self.kwargs)

    def is_null(self):
        return self.func is None


class Worker(Thread):
    def __init__(self, pool):
        self.pool = pool
        super(Worker, self).__init__()
        self.setDaemon()

    @staticmethod
    def spawnNoneJoinableThread(pool):
        worker = Worker(pool)
        worker.start()

    def run(self):
        if __debug__:
            print "[{0}] thread starts".format(self.ident)

        while True:
            task = self.pool.waitForTask()
            if task.is_null():
                break
            task()

        self.pool.decSpawnedThreads()
        if __debug__:
            print "[{0}] thread ends".format(self.ident)

        #actually it is useless
        del self


#threading.Lock supports 'with statement' directly
class ScopedLock(object):
    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        return self.lock.__enter__()
#        self.lock.acquire()
#        return self.lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.lock.__exit__()
#        self.lock.release()
#        return False


class DynamicThreadPool(object):
    def __init__(self, max_worker_threads, max_idle_before_exit, max_capacity=0):
        self.max_worker_threads = max_worker_threads
        self.max_idle_before_exit = max_idle_before_exit
        self.terminated = False

        self.mutex = Mutex()
        self.n_idle_threads = 0
        self.n_spawned_threads = 0

        self.pending_queue = TaskQueue(max_capacity)
        self.pending_queue_convar = ConVar(self.mutex)

    def postTask(self, func, args=(), kwargs={}):
        return self.__addTask(PendingTask(func, args, kwargs))

    def __addTask(self, task):
        assert self.n_spawned_threads >= 0

        with ScopedLock(self.mutex) as lock:
            self.pending_queue.put(task)

            if (self.n_idle_threads < self.pending_queue.size()
                    and self.n_spawned_threads < self.max_worker_threads):
                Worker.spawnNoneJoinableThread(self)
                self.n_spawned_threads += 1
            else:
                self.pending_queue_convar.notify()
        return True

    def waitForTask(self):
        with ScopedLock(self.mutex) as lock:

            left_time = self.max_idle_before_exit
            end_time = time.time() + left_time
            while self.pending_queue.empty() and left_time > 0 and not self.terminated:
                self.n_idle_threads += 1
                self.pending_queue_convar.wait(left_time)
                self.n_idle_threads -= 1
                left_time = end_time - time.time()

            try:
                task = self.pending_queue.pop()
                return task
            except Empty:
                return PendingTask()

    def terminate(self):
        with ScopedLock(self.mutex) as lock:
            if self.terminated:
                return
            self.terminated = True
            self.pending_queue_convar.notifyAll()

    def decSpawnedThreads(self):
        with ScopedLock(self.mutex) as lock:
            self.n_spawned_threads -= 1


if __name__ == "__main__":
    import time
    import random

    def func(*args, **kwargs):
        print '[{0}] starts job'.format(args[0])
        time.sleep(random.randint(1, 10))
        print '[{0}] ends job'.format(args[0])

    pool = DynamicThreadPool(2, 10)
    for i in range(10):
        pool.postTask(func, ('seq %d' % i, i), {'k':i})

    time.sleep(20)
    pool.postTask(func, ('last work', 'last'), {'last':'last'})

    time.sleep(5)
    pool.terminate()

