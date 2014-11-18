#!/usr/bin/env python
#-*- encoding:utf-8 -*-

__author__ = 'fanchao (c.fan@foxmail.com)'
__version__ = '0.0.1'


"""
This defines a OrderedDict class as the same as the OrderedDict in collections module.
Instead of using inexplicable links in python, this class use a index to trace the order of values.

OrderedDict = {key: (index, value), key2: (index2, value2)}.
"""


class OrderedDict(dict):
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise ValueError("'%s' key argument more than one, got: '%d'" % (self.__class__.__name__, len(args)))

        self.index = 0
        new_kwargs = {}
        if args:
            for k, v in args[0].iteritems():
                entry = self.build_entry(v)
                new_kwargs[k] = entry

        if kwargs:
            for k, v in kwargs.iteritems():
                entry = self.build_entry(v)
                new_kwargs[k] = entry

        super(OrderedDict, self).__init__(**new_kwargs)

    def build_entry(self, v):
        entry = (self.index, v)
        self.index += 1
        return entry

    def build_entry_with_index(self, value, index):
        return (index, value)

    def get_entry(self, key, itemget=dict.__getitem__):
        return itemget(self, key)

    def get_entry_value(self, entry):
        return entry[1]

    def get_entry_index(self, entry):
        return entry[0]

    def __setitem__(self, key, value, setitem=dict.__setitem__):
        try:
            entry = self.get_entry(key)
            index = self.get_entry_index(entry)
            new_entry = self.build_entry_with_index(value, index)
            setitem(self, key, new_entry)
        except KeyError:
            setitem(self, key, self.build_entry(value))

    def __getitem__(self, key, getitem=dict.__getitem__):
        return self.get_entry_value(getitem(self, key))

    def iteritems(self):
        for k in self:
            yield (k, self[k])

    def itervalues(self):
        for k in self:
            yield self[k]

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

    def __repr__(self):
        s = ["%r: %r" % (k, v) for k, v in self.iteritems()]

        return 'OrderedDict({%s})' % (','.join(s),)

    def pop(self, key, d=None):
        try:
            return self[key]
        except KeyError as e:
            if not d:
                raise KeyError(e)

        self[key] = d
        return d

    def popitem(self, last=True):
        return sorted([self.get_entry(key) for key in self], key=self.get_entry_index)[0]


if __name__ == '__main__':
    d = OrderedDict({'a':1}, b=2)
    d['a'] = 1
    d['b'] = 2
    d['a'] = 3
    print d
    print d['a']
    print d['b']
    print list(d.iteritems())
    print list(d.iterkeys())
    print list(d.itervalues())

    print d.items()

    del d['a']
    print d.popitem()
    print d.pop('b')
    del d['b']
    print d
