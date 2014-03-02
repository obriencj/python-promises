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
Multi-thread Promises for Python

:author: Christopher O'Brien  <obriencj@gmail.com>
:license: LGPL v.3
"""


from functools import partial
from multiprocessing.pool import ThreadPool
from promises import promise, promise_proxy

import sys


__all__ = ( 'ThreadExecutor', 'ProxyThreadExecutor' )


def _perform_work(work):
    """
    This function is what the worker processes will use to collect the
    result from work (whether via return or raise)
    """

    try:
        return (True, work())
    except Exception as exc:
        return (False, (type(exc), exc, None))


class ThreadExecutor(object):
    """
    A way to provide multiple promises which will be delivered in a
    separate threads
    """


    def __init__(self, threads=None):
        self._threads = threads
        self._pool = None


    def __enter__(self):
        return self


    def __exit__(self, exc_type, _exc_val, _exc_tb):
        """
        Using the managed interface forces blocking delivery at the end of
        the managed segment.
        """

        self.deliver()
        return (exc_type is None)


    def _promise(self):
        """
        override to use a different promise mechanism
        """

        return promise(blocking=True)


    def future(self, work, *args, **kwds):
        """
        Promise to perform work in another process and to deliver the
        result in the future. Returns a container promise with a
        blocking deliver.
        """

        if not self._pool:
            self._pool = ThreadPool(processes=self._threads)

        if args or kwds:
            work = partial(work, *args, **kwds)

        promised,setter,seterr = self._promise()

        def callback(value):
            success, result = value
            if success:
                setter(result)
            else:
                seterr(*result)

        self._pool.apply_async(_perform_work, [work], {}, callback)
        return promised


    def terminate(self):
        """
        breaks all the remaining undelivered promises
        """

        self._pool.terminate()
        self._pool = None


    def deliver(self):
        """
        blocks until all underlying promises have been delivered
        """

        self._pool.close()
        self._pool.join()
        self._pool = None


    def is_delivered(self):
        # TODO better to ask if the pool is empty, check on this
        # later.
        return (self._pool is None)


class ProxyThreadExecutor(ThreadExecutor):
    """
    Creates transparent proxy promises, which will deliver in a
    separate thread
    """

    def _promise(self):
        return promise_proxy(blocking=True)


#
# The end.
