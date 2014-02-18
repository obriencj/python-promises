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
Multi-threaded Promises for Python

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3
"""


from functools import partial
from multiprocessing.pool import ThreadPool
from promises import lazy, lazy_proxy, Container, Proxy
from promises import PromiseNotReady, PromiseAlreadyDelivered


__all__ = ( 'ThreadExecutor', 'ProxyThreadExecutor',
            'promise', 'promise_proxy' )


class ThreadExecutor(object):


    def __promise__(self, work):
        return lazy(work)


    def __init__(self, threads=None):
        self.__pool = None
        self.__threads = threads


    def __enter__(self):
        return self


    def __exit__(self, exc_type, _exc_val, _exc_tb):
        self.deliver()
        return (exc_type is None)


    def future(self, work, *args, **kwds):
        if not self.__pool:
            self.__pool = ThreadPool(processes=self.__threads)

        if args or kwds:
            work = partial(work, *args, **kwds)

        result = self.__pool.apply_async(work, [], {})
        return self.__promise__(result.get)


    def deliver(self):
        self.__pool.close()
        self.__pool is None


    def is_delivered(self):
        return (self.__pool is None)


class ProxyThreadExecutor(ThreadExecutor):

    def __promise__(self, work):
        return lazy_proxy(work)


def _promise(promise_type, blocking=False):

    def promise_getter():
        pass

    promise = promise_type(promise_getter)

    def promise_setter(value):
        pass

    def promise_seterr(exc_type, exc_val, exc_tb):
        pass

    return promise, promise_setter, promise_getter


def promise(blocking=False):
    return _promise(Container, blocking=blocking)


def promise_proxy(blocking=False):
    return _promise(Proxy, blocking=blocking)


#
# The end.
