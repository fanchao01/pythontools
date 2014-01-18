#!/usr/bin/env python
#-*- encoding:utf-8  -*-

__author__ = 'fanchao01'
__version__ = "1.0.0"

"""
Tokenizer is used to split a string with delims.
Each char in delims acts as a delimiter, e.g.
    t = Tokenizer(" abc .def.gh, ", " .")
1.
    t.getNext()  ==>  'abc'
    t.getNext()  ==>  'def'
    t.getNext()  ==>  'gh'
    t.getNext()  ==>  raise EndTokenizerError (no more token)

2.
    for token in t:
        print token
    ==> 'abc'
    ==> 'def'
    ==> 'gh'

"""


class EndTokenizerError(Exception):
    pass


class Tokenizer(object):
    def __init__(self, string, delims):
        self.string = string
        self.delims = delims
        self.begin = self.end = 0

    def reset(self):
        self.begin = self.end = 0

    def getBegin(self):
        return self.begin

    def getEnd(self):
        return self.end

    def getToken(self):
        begin, end = self.getNext()
        return self.string[begin:end]

    def getNext(self):
        skip = 0
        self.begin = self.end
        #skip the chars in delims
        for char in self.string[self.begin:]:
            if self.delims.find(char) == -1:
                break
            skip += 1
        self.begin += skip

        length = 0
        #get the length of one token
        for char in self.string[self.begin:]:
            if self.delims.find(char) != -1:
                break
            length += 1
        if length == 0:
            raise EndTokenizerError("token is end")
        self.end = self.begin + length
        return self.begin, self.end

    def __iter__(self):
        while True:
            try:
                begin, end = self.getNext()
            except EndTokenizerError:
                raise StopIteration
            yield self.string[begin:end]


if __name__ == "__main__":
    t = Tokenizer('  vl abc daef   hagk a  a ', ' a')
    assert list(t) == ['vl', 'bc', 'd', 'ef', 'h', 'gk']
    del t

    t = Tokenizer('     aa       ', ' a')
    try:
        t.getNext()
    except EndTokenizerError:
        pass

