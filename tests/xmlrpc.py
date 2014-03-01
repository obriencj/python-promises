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
from threading import Thread
from unittest import TestCase
from xmlrpclib import ServerProxy
from SimpleXMLRPCServer import SimpleXMLRPCServer


HOST = "localhost"
PORT = 8999


class Dummy(object):
    def __init__(self):
        self.data = list(xrange(0,10))

    def get(self, index):
        return self.data[index]

    def steal(self, index):
        value = self.data[index]
        self.data[index] = None
        return value


class XMLRPCHarness(object):

    def __init__(self, *args, **kwds):
        super(XMLRPCHarness, self).__init__(*args, **kwds)
        self.server = None
        self.dummy = None
        self.thread = None


    def setUp(self):
        assert(self.server is None)
        assert(self.thread is None)

        self.dummy = Dummy()

        self.server = SimpleXMLRPCServer((HOST, PORT))
        self.server.register_function(self.dummy.get, "get")
        self.server.register_function(self.dummy.steal, "steal")
        self.server.register_multicall_functions()

        self.thread = Thread(target=self.server.serve_forever,
                             kwargs={"poll_interval":0.2})
        self.thread.start()


    def tearDown(self):
        assert(self.server is not None)
        assert(self.thread is not None)

        self.server.shutdown()
        self.server.socket.close()
        self.server = None

        self.dummy = None

        self.thread.join()
        self.thread = None


    def get_client(self):
        assert(self.server is not None)
        assert(self.thread is not None)

        return ServerProxy("http://%s:%i" % (HOST,PORT))


class TestLazyMultiCall(XMLRPCHarness, TestCase):


    def get_multicall(self):
        return LazyMultiCall(self.get_client())


    def test_delivery(self):
        mc = self.get_multicall()

        a = mc.steal(1)
        b = mc.steal(2)

        self.assertEqual(deliver(a), 1)
        self.assertEqual(self.dummy.get(1), None)
        self.assertEqual(self.dummy.get(2), None)
        self.assertEqual(deliver(b), 2)


    def test_maxcalls(self):
        mc = self.get_multicall()


class TestProxyMultiCall(TestLazyMultiCall):

    def get_multicall(self):
        return ProxyMultiCall(self.get_client())


#
# The end.
