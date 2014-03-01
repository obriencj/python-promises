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
    """
    A setUp/tearDown harness that will provide an XMLRPC Server for us
    to test against.
    """

    HOST = "localhost"
    PORT = 8999


    def __init__(self, *args, **kwds):
        super(XMLRPCHarness, self).__init__(*args, **kwds)
        self.server = None
        self.thread = None
        self.dummy = None


    def setUp(self):
        assert(self.server is None)
        assert(self.thread is None)

        self.dummy = Dummy()

        self.server = SimpleXMLRPCServer((self.HOST, self.PORT),
                                         logRequests=False)
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

        return ServerProxy("http://%s:%i" % (self.HOST, self.PORT))


class TestLazyMultiCall(XMLRPCHarness, TestCase):


    def get_multicall(self, *args, **kwds):
        return LazyMultiCall(self.get_client(), *args, **kwds)


    def test_delivery(self):
        mc = self.get_multicall()

        a = mc.steal(1)
        b = mc.steal(2)

        # check that the delivery has not yet happened
        self.assertEqual(self.dummy.get(1), 1)
        self.assertEqual(self.dummy.get(2), 2)

        # deliver the first promise and check that the value is what
        # we expected
        self.assertEqual(deliver(a), 1)

        # check that the call happened for both queued promises, which
        # should have destructively altered the dummy entries for
        # those indexes
        self.assertEqual(self.dummy.get(1), None)
        self.assertEqual(self.dummy.get(2), None)

        # check that the second promise has the correct value
        self.assertEqual(deliver(b), 2)


    def test_group_calls(self):
        # have our multicall deliver on promises in groups of 2
        mc = self.get_multicall(group_calls=2)

        # get promises for a bunch of steal calls, each of which has
        # side effects we can test for on the dummy.
        stolen = [mc.steal(x) for x in xrange(0, 10)]

        dummy = self.dummy

        self.assertEqual(deliver(stolen[0]), 0)
        self.assertEqual(dummy.get(0), None)
        self.assertEqual(dummy.get(1), None)
        self.assertEqual(deliver(stolen[1]), 1)

        # having delivered on 0 and 1, 2 should not yet have been
        # delivered, so the dummy 2 should still be 2 rather than None
        self.assertEqual(dummy.get(2), 2)
        self.assertEqual(dummy.get(3), 3)

        self.assertEqual(deliver(stolen[4]), 4)
        self.assertEqual(dummy.get(4), None)
        self.assertEqual(dummy.get(5), None)
        self.assertEqual(deliver(stolen[5]), 5)

        # now having delivered on 4 and 5, 2 should still not yet have
        # been delivered, so the dummy 2 should still be 2 rather than
        # None
        self.assertEqual(dummy.get(2), 2)
        self.assertEqual(dummy.get(3), 3)


    def test_grouped_with(self):

        dummy = self.dummy

        with self.get_multicall(group_calls=3) as mc:
            stolen = [mc.steal(x) for x in xrange(0, 10)]

            # we've collected all the promises, but not delivered yet
            self.assertEqual(dummy.data, list(xrange(0, 10)))

        # now we've delivered, since the managed interface was used
        # and has closed. Thus the desrtuctive steal calls have all
        # happened
        self.assertEqual(dummy.data, ([None] * 10))

        # let's make sure the delivered data is what it should be
        self.assertEqual([deliver(val) for val in stolen],
                         list(xrange(0, 10)))


class TestProxyMultiCall(TestLazyMultiCall):

    def get_multicall(self, *args, **kwds):
        return ProxyMultiCall(self.get_client(), *args, **kwds)


#
# The end.
