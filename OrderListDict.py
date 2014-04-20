#!/usr/bin/env python
# coding: utf-8

"""
OrderList is a list in which elements are sorted as the result of sort() function.
OrderDict is a dict in which the value of the key is the instance of OrderList.The real values are stored in OrderList.
Note that the OrderDict is Not the same as collections.OrderDict.

Both of OrderList/Dict is used as the same as its corresponding part List/Dict.
Because the values of the keys in OrderDict are OrderList, the actual data structure is like belows:
{key1 : OderList(value1, value2, value3), key2: OrderList(value4, value5, value6), ...}
e.g.
>>> od_dict = OrderDict()
>>> od_dict['a'] = 1
>>> od_dict['a'] = 2
>>> od_dict['a'] = 1
>>> od_dict['b'] = 3
>>> od_dict['b'] = 4
>>> od_dict['b'] = 3 #{'a':OrderList(1, 1, 2), 'b':OrderList(3, 3, 4)}
>>> for key, value in od_dict.items(): print key, value
a [1, 1, 2]
b [3, 3, 4]
"""

__author__ = 'fanchao01'
__version__ = '0.1.0'

import bisect
import UserList
import UserDict


class OrderList(UserList.UserList):
    def __init__(self, initlist=None):
        if initlist is not None:
            initlist = sorted(initlist)
        super(OrderList, self).__init__(initlist)

    def insert(self, item):
        bisect.insort_right(self.data, item)

    append = insert


class OrderDict(UserDict.UserDict):
    def __init__(self, dict=None, **kwargs):
        #is old-type class
        new_kwargs = {}
        for key, value in kwargs.items():
            if not isinstance(value, OrderList):
                new_kwargs[key]=OrderList([value])

        UserDict.UserDict.__init__(self, dict, **new_kwargs)

    def __setitem__(self, key, item):
        l = self.data.setdefault(key, OrderList())
        l.append(item)
        
#        if key not in self.data:
#            self.data[key] = OrderList()
#        self.data[key].insert(item)


if __name__ == "__main__":
    import unittest

    class Test(unittest.TestCase):
        def setUp(self):
            self.ol = OrderList()
            self.od = OrderDict()

        def testListInit(self):
            self.assertEqual(OrderList([1, 3, 2, 1]).data, [1, 1, 2, 3])
            self.assertEqual(OrderList((1, 2, 1, 3, 1)).data, [1, 1, 1, 2, 3])

        def testList(self):
            self.ol.insert(1)
            self.ol.insert(100)
            self.ol.insert(50)
            self.ol.insert(1)
            self.ol.insert(100)
            self.assertEqual(self.ol, [1, 1, 50, 100, 100])

        def testDictInit(self):
            od = OrderDict(a=1, b=2)
            self.assertEqual(od, {'a': [1], 'b': [2]})

            od['a'] = 1
            od['b'] = 2
            self.assertEqual(od, {'a': [1, 1], 'b': [2, 2]})

        def testDict(self):
            self.od[1] = 1
            self.assertEqual(self.od, {1: [1]})
            self.od[1] = 1
            self.assertEqual(self.od, {1: [1, 1]})
            self.od[100] = 100
            self.assertEqual(self.od, {1: [1, 1], 100: [100]})
            self.od[50] = 50
            self.assertEqual(self.od.data, {1: [1, 1], 50: [50], 100: [100]})
            self.od[50] = 49
            self.assertEqual(self.od.data, {1: [1, 1], 50: [49, 50], 100: [100]})


    unittest.main()
