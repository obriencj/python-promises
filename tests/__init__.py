# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, see
# <http://www.gnu.org/licenses/>.


"""
Unit Tests for python-promises

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3
"""


import sys
import unittest

from promises import *


def create_exc_tb(exception=None):
    """
    generate an exception info triplet
    """

    if exception is None:
        exception = Exception("dummy exception")

    try:
        raise exception
    except Exception, e:
        return sys.exc_info()


def born_to_fail():
    raise Exception("dummy exception")


class TestContainer(unittest.TestCase):
    """
    tests for the ContainerPromise class
    """


    def lazy(self, work, *args, **kwds):
        return lazy(work, *args, **kwds)


    def promise(self, blocking=False):
        return promise(blocking=blocking)


    def breakable(self, work, *args, **kwds):
        return breakable(work, *args, **kwds)


    def assert_called_once(self, work):
        """
        helper to assert that work is only called once
        """

        called = [False]
        def do_work_once():
            self.assertFalse(called[0], "do_work_once already called")
            called[0] = True
            return work()
        return do_work_once


    def test_promise_setter(self):
        # setter from settable_container delivers

        promised, setter, seterr = self.promise()

        self.assertTrue(is_promise(promised))
        self.assertFalse(is_delivered(promised))

        val = { "testval": True, "a": 5, "b": tuple() }
        setter(val)

        self.assertTrue(is_delivered(promised))
        self.assertEqual(deliver(promised), val)


    def test_promise_seterr(self):
        # seterr from settable_container causes deliver to raise

        promised, setter, seterr = self.promise()

        self.assertTrue(is_promise(promised))
        self.assertFalse(is_delivered(promised))

        class TacoException(Exception):
            pass

        exc = TacoException()
        seterr(*create_exc_tb(exc))

        self.assertRaises(TacoException, lambda: deliver(promised))

        setter(8)
        self.assertTrue(is_delivered(promised))
        self.assertEqual(deliver(promised), 8)


    def test_promise_double_set(self):

        promised, setter, seterr = self.promise()

        self.assertFalse(is_delivered(promised))

        # we aren't ready to deliver, make sure that it says so
        foo = lambda: deliver(promised)
        self.assertRaises(PromiseNotReady, foo)

        setter(100)
        self.assertEqual(deliver(promised), 100)

        # now we try to set it again
        foo = lambda: setter(100)
        self.assertRaises(PromiseAlreadyDelivered, foo)

        # okay, how about setting an exception instead
        foo = lambda: seterr(*create_exc_tb(Exception()))
        self.assertRaises(PromiseAlreadyDelivered, foo)


    def test_memoized(self):
        # promised work is only executed once.

        work = self.assert_called_once(lambda: "Hello World")
        promised = self.lazy(work)

        self.assertEqual(deliver(promised), "Hello World")
        self.assertEqual(deliver(promised), "Hello World")


    def test_callable_int(self):
        # callable work returning an int

        promised = self.lazy(lambda: 5)

        self.assertTrue(is_promise(promised))
        self.assertFalse(is_delivered(promised))

        x = deliver(promised) + 1
        self.assertTrue(is_delivered(promised))
        self.assertEqual(deliver(promised), 5)
        self.assertEqual(x, 6)


    def test_non_callable_int(self):
        # int as promised work delivers immediately

        promised = self.lazy(5)

        self.assertTrue(is_promise(promised))
        self.assertTrue(is_delivered(promised))

        x = deliver(promised) + 1
        self.assertTrue(is_delivered(promised))
        self.assertEqual(deliver(promised), 5)
        self.assertEqual(x, 6)


    def test_repr(self):
        promised = self.lazy(lambda: 5)
        self.assertEqual("<promises.Container undelivered>",
                         promise_repr(promised))

        deliver(promised)

        self.assertEqual("<promises.Container delivered:5>",
                         promise_repr(promised))

        promised = self.breakable(born_to_fail)
        self.assertEqual("<promises.Container undelivered>",
                         promise_repr(promised))

        deliver(promised)

        self.assertEqual("<promises.Container broken>",
                         promise_repr(promised))

        self.assertEqual("5", promise_repr(5))


    def test_broken(self):
        # test that a breakable that doesn't break will function
        # correctly
        promised = self.breakable(lambda: 5)
        self.assertTrue(is_promise(promised))
        self.assertFalse(is_delivered(promised))

        deliver(promised)
        self.assertTrue(is_delivered(promised))
        self.assertEqual(deliver(promised), 5)

        # create a breakable that will definitely break
        promised = self.breakable(born_to_fail)
        self.assertTrue(is_promise(promised))
        self.assertFalse(is_delivered(promised))

        # breakable promises count as delivered if they break, but
        # they return a BrokenPromise instance
        deliver(promised)
        self.assertTrue(is_delivered(promised))
        self.assertTrue(isinstance(deliver(promised), BrokenPromise))


    def test_breakable_deliver(self):
        # a promise that will definitely fail
        promised = self.lazy(born_to_fail)
        self.assertTrue(is_promise(promised))
        self.assertFalse(is_delivered(promised))

        # check that delivery does indeed raise an Exception and
        # doesn't cause the delivery to take.
        self.assertRaises(Exception, lambda: deliver(promised))
        self.assertFalse(is_delivered(promised))

        # attempt breakable delivery. Should not raise, but should
        # instead return a BrokenPromise. Since the promise wasn't
        # created breakable, it will still not count as delivered.
        broken = breakable_deliver(promised)
        self.assertTrue(isinstance(broken, BrokenPromise))
        self.assertFalse(is_delivered(promised))


class TestProxy(TestContainer):
    """
    tests for the ProxyPromise class
    """


    def lazy(self, work, *args, **kwds):
        return lazy_proxy(work, *args, **kwds)


    def promise(self, blocking=False):
        return promise_proxy(blocking=blocking)


    def breakable(self, work, *args, **kwds):
        return breakable_proxy(work, *args, **kwds)


    def test_proxy_equality(self):
        # proxy equality works over a wide range of types

        class DummyClass(object):
            pass

        values = ( True, False,
                   999, 9.99, "test string", u"unicode string",
                   (1, 2, 3), [1, 2, 3],
                   {"a":1,"b":2,"c":3},
                   object, object(), DummyClass, DummyClass(),
                   xrange, xrange(0, 99),
                   lambda x: x+8 )

        provs = [self.lazy(lambda:val) for val in values]

        for val,prov in zip(values, provs):
            self.assertEqual(prov, val)
            self.assertEqual(val, prov)


    def test_proxy_int(self):
        # transparent proxy of an int

        A = 5
        B = self.lazy(5)
        deliver(B)

        self.assertTrue(A == B)
        self.assertTrue(B == A)
        self.assertTrue((A + B) == 10)
        self.assertTrue((B + A) == 10)
        self.assertTrue((B * 2) == 10)
        self.assertTrue((2 * B) == 10)
        self.assertTrue((str(B)) == "5")
        self.assertTrue((int(B)) == 5)
        self.assertTrue((B % 1) == (5 % 1))
        self.assertTrue((B >> 1) == (5 >> 1))
        self.assertTrue((B << 1) == (5 << 1))
        self.assertTrue((B ** 2) == (5 ** 2))


    def test_proxy_obj(self):
        # transparent proxy of an object

        class Foo(object):
            A = 100
            def __init__(self):
                self.B = 200
            def C(self):
                return 300
            def __eq__(self, o):
                return (self.A == o.A and
                        self.B == o.B and
                        self.C() == o.C())
            def __ne__(self, o):
                return not self.__eq__(o)

        FA = Foo()
        FB = self.lazy(Foo)

        deliver(FB)
        self.assertTrue(FA == FB)
        self.assertTrue(FB == FA)

        FA.B = 201
        FB.B = 201
        self.assertTrue(FA == FB)
        self.assertTrue(FB == FA)


    def test_repr(self):
        promised = self.lazy(lambda: 5)
        self.assertEqual("<promises.Proxy undelivered>",
                         promise_repr(promised))

        deliver(promised)

        self.assertEqual("<promises.Proxy delivered:5>",
                         promise_repr(promised))

        promised = self.breakable(born_to_fail)
        self.assertEqual("<promises.Proxy undelivered>",
                         promise_repr(promised))

        deliver(promised)

        self.assertEqual("<promises.Proxy broken>",
                         promise_repr(promised))


#
# The end.
