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


from promises.multiprocess import ProcessExecutor, ProxyProcessExecutor
from unittest import TestCase


def work_load(x):
    return x + 1


class TestProcessExecutor(TestCase):


    def executor(self):
        return ProcessExecutor()


    def test_parallel(self):
        with self.executor() as E:
            a = E.future(work_load, -1)
            values = [E.future(work_load, x) for x in xrange(0, 999)]
            b = E.future(work_load, -101)

        self.assertTrue(is_promise(a))
        self.assertTrue(is_delivered(a))
        self.assertEqual(deliver(a), 0)

        self.assertTrue(is_promise(b))
        self.assertTrue(is_delivered(b))
        self.assertEqual(deliver(b), -100)

        self.assertEqual([deliver(v) for v in values],
                         list(xrange(1, 1000)))


class TestProxyProcessExecutor(TestProcessExecutor):

    def _executor(self):
        return ProxyProcessExecutor()


#
# The end.
