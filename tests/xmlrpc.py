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


from abc import abstractmethod, ABCMeta
from promises import *
from promises.xmlrpc import *
from unittest import TestCase


class TestBaseMultiCall(object):
    
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwds):
        super(TestBaseMultiCall, self).__init__(*args, **kwds)
        self.server = None

    def get_server(self):
        return self.server

    @abstractmethod
    def multicall(self, server):
        return None


    def test_constructor(self):
        mc = self.multicall(None)


    def test_maxcalls(self):
        mc = self.multicall(self.get_server())


class TestContainerMultiCall(TestBaseMultiCall, TestCase):
    def multicall(self, server):
        return ContainerMultiCall(server)


class TestProxyMultiCall(TestBaseMultiCall, TestCase):
    def multicall(self, server):
        return ProxyMultiCall(server)


#
# The end.

