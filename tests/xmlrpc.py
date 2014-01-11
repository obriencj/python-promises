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

Unit-tests for python-promises XML RPC MultiCall

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3

"""


from promises import *
from promises.xmlrpc import *
from unittest import TestCase


class TestLazyMultiCall(TestCase):

    def __init__(self, *args, **kwds):
        super(TestLazyMultiCall, self).__init__(*args, **kwds)
        self.server = None


    def multicall(self):
        return LazyMultiCall(self.server)


    def get_server(self):
        return self.server


    def test_constructor(self):
        mc = self.multicall()


    def test_maxcalls(self):
        mc = self.multicall()


class TestProxyMultiCall(TestLazyMultiCall):

    def multicall(self):
        return ProxyMultiCall(self.server)


#
# The end.

