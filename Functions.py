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


#send_email is a easy function for sending a mail wihout login needed
from smtplib import SMTP
from email.MIMEText import MIMEText


class SendMailError(Exception):
    pass


def send_mail(frm, to, subject, content, content_type='palin', server='localhost', port=25):
    if isinstance(to, basestring):
        to = [to]

    try:
        msg = MIMEText(content,  content_type, 'utf-8')
        msg['Subject'] = subject
        msg['From'] = frm

        conn = SMTP(server, 25)
        conn.set_debuglevel(False)
#        conn.login(username, password)
        try:
            conn.sendmail(frm, to, msg.as_string())
        finally:
            conn.quit()

    except Exception as exc:
        raise SendMailError(exc)


#a mandatory curring method to be a replace of functools.partial.
#for functools.partial is a type, it can not be used for methods in a class
def curry(_curried_func, *args, **kwargs):
    def _curry(*moreargs, **morekwargs):
        return _curried_func(*(args + moreargs), **dict(kwargs, **morekwargs))
    return _curry


#given a list of data, generate a itertor of indices of the slice in the give step
#combinations(range(3), 1) ==> ((0, 1), (1, 2))
#combinations(range(6), 2) ==> ((0, 2), (2, 4), (4, None))
import itertools


def combinations(lst, step=1):
    return itertools.izip(lst[::step], lst[step::step] + [None,])


if __name__ == '__main__':
    f = get_fields("cpu0 0 1 2\ncpu1 3 4 5\ncpu1 6 7 8", [0, 2], 'cpu1')
    print f

    print tuple(combinations(range(6), 2))

