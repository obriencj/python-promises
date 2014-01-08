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


import unittest

from promises import *


class TestContainerPromise(unittest.TestCase):

    def testFoo(self):
        
        promise, setter, seterr = settable_container()
        assert(is_promise(promise))
        assert(not is_delivered(promise))

        val = { "testval": True, "a": 5, "b": tuple() }
        setter(val)
        assert(is_delivered(promise))

        assert(deliver(promise) == val)


class TestProxyPromise(unittest.TestCase):

    def test_settable(self):

        promise, setter, seterr = settable_proxy()
        assert(is_promise(promise))
        assert(not is_delivered(promise))

        val = { "testval": True, "a": 5, "b": tuple() }
        setter(val)
        assert(is_delivered(promise))

        assert(promise == val)


#
# The end.
