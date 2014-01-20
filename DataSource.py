#!/usr/bin/env python
#-*- encoding:utf-8 -*-

"""
Source class is a manger of directory.

update() function is used to update the directory to collect new files.
hasNextFile() function is used to check if there is a next file.
getNextFile() just returns the self.curr_filename, which updated by hasNextFile if existed.

Notice:
update() function just called once at initial,
so the files created after the instantiation of Source will not be included.
update() should be called to get these files or to make sure there are no more files to deal with in the directory.
e.g.
    s = Source('.')
    ...
    if s.hasNextFile():
        next = s.getNextFile()
        if next is None:
            s.update()
            if s.hasNextFile():  #again
                next = s.getNextFile()      #get files created after the instantiation of Source
            else:
                print 'no valid file to deal with'      #or make sure there are no more files

TODO:
1. Calling update() by users is a good idea?
2. read method and progress record added into Source class
"""


__author__ = 'fanchao01'
__version__ = '0.0.1'

import os


class Source(object):
    def __init__(self, dirname=None, sorted_as_mtime=True):
        self.dirname = dirname
        self.sorted_as_mtime = sorted_as_mtime

        self.curr_filename = None
        self.update()

    def update(self):
        self.files = os.listdir(self.dirname)
        self.files = [os.path.join(self.dirname, fname) for fname in self.files]
        self.files = [fname for fname in self.files if os.path.isfile(fname)]
        if self.sorted_as_mtime:
            self.files = sorted(self.files, key=lambda x: os.stat(x).st_mtime)

        if __debug__:
            print self.files

    def hasNextFile(self):
        if self.curr_filename:
            if self.sorted_as_mtime:
                findfunc = lambda x, y: os.stat(x).st_mtime < os.stat(y).st_mtime
            else:
                findfunc = lambda x, y: x < y

            for fname in self.files:
                if findfunc(self.curr_filename, fname):
                    self.curr_filename = fname
                    return True
            else: #do not find valid file
                return False

        if self.files:
            self.curr_filename = self.files[0]
            return True
        else:
            return False

    def getNextFile(self):
        if self.hasNextFile():
            return self.curr_filename

        return None

    def __iter__(self):
        while True:
            next_file = self.getNextFile()
            if next_file is None:
                raise StopIteration
            yield next_file


if __name__ == "__main__":
    s = Source(".", False)
#    s = Source(".", True)
    for i, fname in enumerate(s):
        print "{0} : {1}".format(i, fname)

