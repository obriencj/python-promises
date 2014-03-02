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
Unit-tests for python-promises multiprocessing support

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3
"""


from promises import is_promise, is_delivered, deliver
from promises.multiprocess import ProcessExecutor, ProxyProcessExecutor
from unittest import TestCase


def work_load(x):
    #print "performing work_load", x
    return x + 1


def fail_load(x):
    #print "fail_load raising"
    raise TacoException("failed on %i" % x)


class TacoException(Exception):
    pass


class TestProcessExecutor(TestCase):


    def executor(self):
        return ProcessExecutor()


    def test_managed(self):
        with self.executor() as ex:
            a = ex.future(work_load, -1)
            self.assertTrue(is_promise(a))

            # generate some minor workload, enough to engage a queue
            values = [ex.future(work_load, x) for x in xrange(0, 999)]

            b = ex.future(work_load, -101)
            self.assertFalse(is_delivered(b))

        # the managed interface implicitly calls the deliver() method
        # on the executor, so by the time we get here, everything
        # should be delivered.

        self.assertTrue(is_promise(a))
        self.assertTrue(is_delivered(a))
        self.assertEqual(deliver(a), 0)

        self.assertTrue(is_promise(b))
        self.assertTrue(is_delivered(b))
        self.assertEqual(deliver(b), -100)

        self.assertEqual([deliver(v) for v in values],
                         list(xrange(1, 1000)))


    def test_blocking(self):
        ex = self.executor()

        # generate some minor workload, enough to engage a queue
        values = [ex.future(work_load, x) for x in xrange(0, 999)]

        b = ex.future(work_load, -101)
        self.assertFalse(is_delivered(b))
        self.assertEqual(deliver(b), -100)

        ex.deliver()
        #self.assertTrue(ex.is_delivered())


    def test_terminate(self):
        ex = self.executor()

        # generate some minor workload, enough to engage a queue
        values = [ex.future(work_load, x) for x in xrange(0, 999)]

        b = ex.future(work_load, -101)
        self.assertFalse(is_delivered(b))

        ex.terminate()
        self.assertFalse(is_delivered(b))

        #self.assertTrue(ex.is_delivered())


    def test_raises(self):
        ex = self.executor()

        # generate some minor workload, enough to engage a queue
        values = [ex.future(work_load, x) for x in xrange(0, 999)]

        b = ex.future(fail_load, -101)

        self.assertFalse(is_delivered(b))
        self.assertRaises(TacoException, lambda: deliver(b))

        ex.terminate()


class TestProxyProcessExecutor(TestProcessExecutor):

    def executor(self):
        return ProxyProcessExecutor()


#
# The end.
