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

Promises for Python

Yet another module for doing promises in python! This time with
transparent proxies, and other convoluted stuff that will make you
wish someone smarter had worked on this.

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3

"""


import _proxy
from _proxy import ProxyPromise


class ContainerPromise(object):
    
    """ Simplest promise mechanism. Will invoke a work function
    exactly once, and deliver the result as many times as
    necessary. """

    def __init__(self, work):
        if callable(work):
            self._work = work
            self._answer = None
        else:
            self._work = None
            self._answer = work

    def __del__(self):
        self._work = None
        self._answer = None

    def is_promise(self):
        return True

    def is_delivered(self):
        return self._work is None

    def deliver(self):
        if self._work is not None:
            self._deliver()
        return self._answer
           
    def _deliver(self):
        # in theory this could be overridden to change how delivery
        # occurs, but it's probably better to use special workers
        # instead.
        assert(self._work is not None)
        self._answer = self._work()
        self._work = None


def is_promise(obj):
    """ True if obj is a promise (either a proxy or a container) """

    return (_proxy.is_proxy(obj) or
            isinstance(obj, ContainerPromise))


def is_delivered(obj):
    """ True if a promise has been delivered """

    return _proxy.is_proxy_delivered(obj) if _proxy.is_proxy(obj) \
        else obj.is_delivered()


def deliver(obj):
    """ attempts to deliver a promise """

    return _proxy.deliver_proxy(obj) if _proxy.is_proxy(obj) \
        else obj.deliver()


class PromiseNotReady(Exception):
    """ Raised when attempting to deliver on a promise whose
    underlying delivery function hasn't been called (see
    container_pair and proxy_pair) """
    pass


class PromiseAlreadyDelivered(Exception):
    """ Raised when a paired promise's delivery function is called
    more than once (see container_pair and proxy_pair) """
    pass


def _settable_promise(promise_type):

    """ This is the 'traditional' type of promise. It's a single-slot,
    write-once value. I like mine better. But check it out, mine can
    turn into the boring one with the greatest of ease! """

    # our shared state! trololol closures
    ptr = list()
    exc = list()
    
    def promise_getter():
        if ptr:
            return ptr[0]
        elif exc:
            raise exc[0], exc[1], exc[2]
        else:
            raise PromiseNotReady()

    promise = promise_type(promise_getter)

    def promise_setter(value):
        if ptr:
            raise PromiseAlreadyDelivered()
        else:
            exc.clear()
            ptr.append(value)
            deliver(promise)

    def promise_exc(exc_type, exc_val, exc_tb):
        if ptr:
            raise PromiseAlreadyDelivered()
        else:
            exc.clear()
            exc.extend((exc_type, exc_val, exc_tb))

    return (promise, promise_setter, promise_exc)


def settable_container():

    """ Returns a tuple of a new ContainerPromise and a unary function
    to deliver a value into that promise """

    return _settable_promise(ContainerPromise)


def settable_proxy():

    """ Returns a tuple of a new ProxyPromise and a unary function to
    deliver a value into that promise """

    return _settable_promise(ProxyPromise)


def _settable_blocking_promise(promise_type):
    
    from threading import Event

    ptr = list()
    exc = list()
    event = Event()

    def promise_getter():
        event.wait()
        if ptr:
            return ptr[0]
        elif exc:
            raise exc[0], exc[1], exc[2]
        else:
            raise PromiseNotReady()

    promise = promise_type(promise_getter)

    def promise_setter(value):
        if ptr:
            raise PromiseAlreadyDelivered()
        else:
            exc.clear()
            ptr.append(value)
            event.set()
            deliver(promise)
    
    def promise_exc(exc_type, exc_val, exc_tb):
        if ptr:
            raise PromiseAlreadyDelivered()
        else:
            exc.clear()
            exc.extend((exc_type, exc_val, exc_tb))

    return (promise, promise_setter, promise_exc)


def settable_blocking_container():
    return _settable_blocking_promise(ContainerPromise)


def settable_blocking_proxy():
    return _settable_blocking_promise(ProxyPromise)


#
# The end.
