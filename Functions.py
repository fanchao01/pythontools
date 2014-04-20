#!/usr/bin/env python
# -*- encoding:utf-8 -*-

__author__ = 'fanchao01'
__version__ = '0.0.1'

all = ['wcl', 'cxx_files_lines_count']


#wcl is a function like bask commands 'wc -l'
def wcl(path, ext=None, depth=None, followlinks=False):
    filt = lambda f: os.path.splitext(f)[-1] in ext if ext else None

    nlines = 0
    for root, dirs, files in os.walk(top=path, followlinks=followlinks):
        #depth is None or <= 0: recursive.
        if depth is None or depth <= 0 or (root.count(os.path.sep) < depth):
            if filt:
                files = filter(filt, files)
            for f in files:
                with open(os.path.join(root, f), 'r') as infile:
                    nlines += infile.read().count('\n')

                if __debug__:
                    print f

    return nlines


cxx_files_lines_count = lambda path: wcl(path, ('.cpp', '.ccp', '.cc', '.c', '.h', '.hpp'))


#get_field is a function like grep -E '^linestart' |cut -d'sep' -ffield
import re
import operator     #2.6+ supported


def get_fields(data, fields,  linestart="", sep=" "):
    """
Parse data from string
@param data: Data to parse
example:
    data:
        cpu 1 2 3 4
        cpu0 5 6 7 8
        cpu1 9 10 11 12
        linestart filed 0 1 2 3
@param field: Position of data after linestart
@param linestart: String to which start line
@param sp: separator between parameters regular expression

@exception: raise IndexError when the corresponding fields do not exist
"""
    getter = operator.itemgetter(*fields)
    search = re.compile(r'(?<=^%s)\s+(.*)' % linestart, re.MULTILINE)
    find = search.search(data)
    if find is not None:
        return getter(re.split("%s" % sep, find.group(1)))
    else:
        return ()


if __name__ == '__main__':
    f = get_fields("cpu0 0 1 2\ncpu1 3 4 5\ncpu1 6 7 8", [0, 2], 'cpu1')
    print f

