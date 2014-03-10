#!/usr/bin/env python
#-*- encoding:gb2312 -*- 

'''
���뷽ʽgb2312�Ա�֧������ע�͡�

thread.lock��һ�����������lock(pthread lock)��
������ͬһ�����ᵼ������״̬���ͷ�һ��������ס״̬��lock�ᵼ��error��

AtExitManager ���� atexitģ�飬֧�ֶ��̡߳� Stackû������Ԫ�ص�������
'''

import threading


#ScopedLockû��ʲô�ã�thread.lock����֧��with��䡣
class ScopedLock(object):
    def __init__(self, mutex):
        self._mutex = mutex;

    def __enter__(self):
        self._mutex.acquire()

    def __exit__(self, type, value, traceback):
        if self._mutex.locked():
            self._mutex.release()
            return True

    def __del__(self):
        if self._mutex.locked():
            self._mutex.release()
        


class Stack(object):
    def __init__(self, mutex, initlist=None):
        self._list = []
        self._mutex = mutex
        if initlist is not None:
            self._list.extend(initlist)
    
    def __iter__(self):
        while self._list:
            yield self.pop()

    def __len__(self):
        return len(self._list)

    def push(self, item):
        with ScopedLock(self._mutex):
            self._list.insert(0, item)
        return len(self._list)

    def pop(self):
        with ScopedLock(self._mutex):
            return self._list.pop()
        


class Task(object):
    def __init__(self, func, *args):
        self._func = func or None
        self._args = args
    def __call__(self):
        assert(self._func is not None)
        return self._func(*self._args)



class AtExitManager(object):
    def __init__(self, mutex=None) :
        self._mutex = mutex or threading.Lock()
        self._stack = Stack(self._mutex)

    def __len__(self):
        return len(self._stack)

    def registerCallback(self, func, *args):
        self._stack.push(Task(func, *args))

    def registerTask(self, task):
        self._stack.push(task)

    def processTasks(self):
        for task in self._stack:
            task()

    def __call__(self):
        self.processTasks()


global_manager = AtExitManager()

if __name__ == "__main__":
    def func(*args):
        print args
    task = Task(func, 1, 2, 3)
    task()
    del task

    mutex = threading.Lock()
    with ScopedLock(mutex):
        assert(mutex.locked())
    assert(mutex.locked() is False)

    stack = Stack(mutex)
    del mutex
    del stack

    at = global_manager
    at.registerCallback(func, 1)
    at.registerTask(Task(func, 2))
    assert(len(at) == 2)
    at()

