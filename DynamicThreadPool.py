#!/usr/bin/env python
#-*- encoding:utf-8 -*-
"""
DynamicThreadPool is a pool of dynamic threads. It could create and destroy the worker thread dynamically.
e.g.
    pool = DynamicThreadPool(2, 10)
    for i in range(100):
        pool.post_task(func, *args, **kwargs)

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
import time
import logging
import Queue

from threading import Thread
from threading import RLock as Mutex, Condition as ConVar


threads_pool = None


class PendingTask(object):
    def __init__(self, func=None, args=None, kwargs=None):
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.func = func

    def __call__(self):
        return self.func(*self.args, **self.kwargs)

    def is_over(self):
        return self.func is None


class Worker(Thread):
    def __init__(self, pool):
        self.pool = pool
        super(Worker, self).__init__()
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
            if task.is_over():
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

        self.pending_queue = Queue.Queue(max_capacity)
        self.pending_queue_convar = ConVar(self.mutex)

        global threads_pool
        threads_pool = self

    def post_task(self, func, args=None, kwargs=None):
        args = args or ()
        kwargs = kwargs or {}
        logging.debug("post task, func: {0} args: {1}, kwargs: {2}"
                      .format(func, args, kwargs))
        return self._add_task(PendingTask(func, args, kwargs))

    def _add_task(self, task):
        assert self.n_spawned_threads >= 0

        with self.mutex as lock:
            self.pending_queue.put(task)

            if (self.n_idle_threads < self.pending_queue.qsize()
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
                task = self.pending_queue.get_nowait()
                return task
            except Queue.Empty:
                return PendingTask()

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
        time.sleep(random.randint(1, 3))
        print '[{0}] ends job'.format(args[0])

    pool = DynamicThreadPool(100, 10)
    for i in range(10):
        pool.post_task(func, ('seq %d' % i, i), {'k':i})

    time.sleep(20)
    pool.post_task(func, ('last work', 'last'), {'last':'last'})

    time.sleep(5)
    pool.terminate()

