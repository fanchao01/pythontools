#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
Duration is the time delta class like the datetime.timedelta in standard library.
But Duration could be initialized with d = Duration(days=1, minutes=2), 
or with d.seconds=1. while the timedelta only could be with one argument in second.

All Duration and Time class has the precision of milliseconds.
Except Time.clock has the real precision of time.clock (gettimeofday in unix-like system).

Please use time.strptime, time.strftime and so on to format the Time.
"""
from __future__ import division
from functools import total_ordering

import time


__all__ = ['Duration', 'Time']


class TIME(object):
    MSECONDS_PER_MSECONDS = 1
    MSECONDS_PER_SECOND = 1000
    MSECONDS_PER_MINUTE = 60000
    MSECONDS_PER_HOUR = 3600000
    MSECONDS_PER_DAY = 86400000

    _TO_MSECONDS={'mseconds': MSECONDS_PER_MSECONDS,
                  'seconds': MSECONDS_PER_SECOND,
                  'minutes': MSECONDS_PER_MINUTE,
                  'hours': MSECONDS_PER_HOUR,
                  'days': MSECONDS_PER_DAY,
                  }

    _MSECONDS_TO={'mseconds': 1/MSECONDS_PER_MSECONDS,
                  'seconds': 1/MSECONDS_PER_SECOND,
                  'minutes': 1/MSECONDS_PER_MINUTE,
                  'hours': 1/MSECONDS_PER_HOUR,
                  'days': 1/MSECONDS_PER_DAY
                }


class TimeDescriptor(object):
    def __init__(self, ratio):
        self.ratio = ratio

    def __get__(self, instance, owner):
        return instance._mseconds / self.ratio

    def __set__(self, instance, value):
        instance._mseconds = value * self.ratio

    def __delete__(self, instance):
        instance._mseconds = 0


class Tzname(object):
    def __get__(self, instance, owner):
        return time.tzname

    def __set__(self, instance, value):
        time.tzname = value


class StructTime(object):
    def __get__(self, instance, owner):
        print instance.seconds
        return time.localtime(instance.seconds)


@total_ordering
class Duration(object):
    def __new__(cls, **kwargs):
        for unit, ratio in TIME._TO_MSECONDS.items():
            setattr(cls, unit, TimeDescriptor(ratio))

        return object.__new__(cls)

    def __init__(self,
                 days=0,
                 hours=0,
                 minutes=0,
                 seconds=0,
                 mseconds=0):

        
        self._mseconds = (
            TIME.MSECONDS_PER_DAY * days +
            TIME.MSECONDS_PER_HOUR * hours +
            TIME.MSECONDS_PER_MINUTE * minutes +
            TIME.MSECONDS_PER_SECOND * seconds +
            TIME.MSECONDS_PER_MSECONDS * mseconds
        )

    def __repr__(self):
        return '<Duration Sec: %0.3f>' % self._mseconds

    def __add__(self, other):
        sum_mseconds = self._mseconds + other._mseconds
        return Duration(mseconds=sum_mseconds)

    def __sub__(self, other):
        if self._mseconds < other._mseconds:
            raise ValueError("'%s' less than '%s'" % (self, other))

        sub_mseconds = self._mseconds - other._mseconds
        return Duration(mseconds=sub_mseconds)

    def __mul__(self, mul):
        ms = self._mseconds * mul
        return Druation(mseconds=ms)

    def __div__(self, div):
        ms = self._mseconds / div
        return Druation(mseconds=ms)

    def __iadd__(self, other):
        self._mseconds += other._mseconds
        return self

    def __isub__(self, other):
        if self._mseconds < other._mseconds:
            raise ValueError('')
        self._mseconds -= other._mseconds
        return self

    def __imul__(self, mul):
        self._mseconds *= mul
        return self

    def __idiv__(self, div):
        self._mseconds /= div
        return self

    def __eq__(self, other):
        return self._mseconds == other._mseconds

    def __gt__(self, other):
        return self._mseconds > other._mseconds

    #either time.sleep(Duration(1)), or Duration(1).sleep()  is Ok
    def __float__(self):
        return self.seconds

    def sleep(self):
        return time.sleep(self.seconds)


@total_ordering
class Time(object):
    def __new__(cls, **kwargs):
        tzname = Tzname()
        struct_time = StructTime()
        for unit, ratio in TIME._TO_MSECONDS.items():
            setattr(cls, unit, TimeDescriptor(ratio))
        
        setattr(cls, 'tzname', Tzname())
        setattr(cls, 'struct_time', StructTime())


        return object.__new__(cls)

    def __init__(self,
                 days=0,
                 hours=0,
                 minutes=0,
                 seconds=0,
                 mseconds=0):

        self._mseconds = (
            TIME.MSECONDS_PER_DAY * days +
            TIME.MSECONDS_PER_HOUR * hours +
            TIME.MSECONDS_PER_MINUTE * minutes +
            TIME.MSECONDS_PER_SECOND * seconds +
            TIME.MSECONDS_PER_MSECONDS * mseconds
        )

    @staticmethod
    def now():
        return Time(seconds=time.time())

    def __add__(self, duration):
        ms = self._mseconds + duration._mseconds
        return Time(mseconds=ms)

    def __sub__(self, d):
        if self._mseconds < d._mseconds:
            raise ValueError("'%s' less than '%s'" % (self, d))

        sub = self._mseconds - d._mseconds
        if isinstance(d, Duration):
            return Time(mseconds=sub)
        else:
            return Duration(mseconds=sub)

    def __repr__(self):
        return '<Time Sec: %0.3f>' % self.seconds

    def __eq__(self, other):
        return self._mseconds == other._mseconds

    def __gt__(self, other):
        return self._mseconds > other._mseconds


    @staticmethod
    def clock():
        return time.clock()


if __name__ == '__main__':
    d = Duration(days=1, mseconds=0.1)
    print d.days
    print d.hours
    print (d + d).hours
    print (d - d).minutes
    print d
    d += d
    d -=d
    print d

    t = Time.now()
    print t.mseconds
    print t.seconds
    print t.struct_time
    print t-t
    print t-d
    print t == t

    tt = t + Duration(mseconds=1)
    try:
        t - tt
    except ValueError as e:
        print e.message

    time.sleep(Duration(seconds=1))
    Duration(mseconds=1).sleep()
