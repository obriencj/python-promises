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


def assert_called_once(work):
    """ helps assert that work is only called once """

    called = [False]
    def do_work_once():
        assert(called[0] is False)
        called[0] = True
        return work()
    return do_work_once


def create_exc_tb(exception=None):
    """ generate an exception info triplet """

    if exception is None:
        exception = Exception("dummy exception")

    try:
        raise exception
    except Exception, e:
        return sys.exc_info()


class TestContainer(unittest.TestCase):

    """ tests for the ContainerPromise class """


    def lazy(self, work, *args, **kwds):
        return lazy(work, *args, **kwds)


    def promise(self):
        return promise()


    def test_promise_setter(self):
        # setter from settable_container delivers

        promised, setter, seterr = self.promise()

        assert(is_promise(promised))
        assert(not is_delivered(promised))

        val = { "testval": True, "a": 5, "b": tuple() }
        setter(val)

        assert(is_delivered(promised))
        assert(deliver(promised) == val)


    def test_promise_seterr(self):
        # seterr from settable_container causes deliver to raise

        promised, setter, seterr = self.promise()

        assert(is_promise(promised))
        assert(not is_delivered(promised))

        exc = Exception("test_settable_err")
        seterr(*create_exc_tb(exc))

        try:
            deliver(promised)
        except Exception, e:
            assert(e == exc)
        else:
            # deliver had darn well better raise that exception
            assert(False)

        setter(8)
        assert(is_delivered(promised))
        assert(deliver(promised) == 8)


    def test_memoized(self):
        # promised work is only executed once.

        work = assert_called_once(lambda: "Hello World")
        promised = self.lazy(work)

        assert(deliver(promised) == "Hello World")
        assert(deliver(promised) == "Hello World")


    def test_callable_int(self):
        # callable work returning an int

        promised = self.lazy(lambda: 5)

        assert(is_promise(promised))
        assert(not is_delivered(promised))

        x = deliver(promised) + 1
        assert(is_delivered(promised))
        assert(deliver(promised) == 5)
        assert(x == 6)


    def test_non_callable_int(self):
        # int as promised work delivers immediately

        promised = self.lazy(5)

        assert(is_promise(promised))
        assert(is_delivered(promised))

        x = deliver(promised) + 1
        assert(is_delivered(promised))
        assert(deliver(promised) == 5)
        assert(x == 6)


class TestProxy(TestContainer):

    """ tests for the ProxyPromise class """


    def lazy(self, work, *args, **kwds):
        return lazy_proxy(work, *args, **kwds)


    def promise(self):
        return promise_proxy()


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
            assert(prov == val), "%r != %r" % (prov, val)
            assert(val == prov), "%r != %r" % (val, prov)


    def test_proxy_int(self):

        A = 5
        B = self.lazy(5)
        deliver(B)

        assert(A == B)
        assert(B == A)
        assert((A + B) == 10)
        assert((B + A) == 10)
        assert((B * 2) == 10)
        assert((2 * B) == 10)
        assert((str(B)) == "5")
        assert((int(B)) == 5)
        assert((B % 1) == (5 % 1))
        assert((B >> 1) == (5 >> 1))
        assert((B << 1) == (5 << 1))
        assert((B ** 2) == (5 ** 2))


    def test_proxy_obj(self):
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
        assert(FA == FB)
        assert(FB == FA)

        FA.B = 201
        FB.B = 201
        assert(FA == FB)
        assert(FB == FA)


#
# The end.
