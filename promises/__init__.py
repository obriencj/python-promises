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


from _proxy import ProxyPromise
from _proxy import is_proxy, is_proxy_delivered, deliver_proxy
from threading import Event


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

    def is_delivered(self):
        return self._work is None

    def deliver(self):
        # in theory this could be overridden to change how delivery
        # occurs, but it's probably better to use special workers
        # instead.

        work = self._work

        if work is not None:
            # note that if the work raised an exception, we won't
            # consider ourselves as delivered, meaning we can attempt
            # delivery again later. This is a feature!
            self._answer = work()
            self._work = None

        return self._answer


def is_promise(obj):
    """ True if obj is a promise (either a proxy or a container) """

    return (is_proxy(obj) or \
                (hasattr(obj, "is_delivered") and
                 hasattr(obj, "deliver")))


def is_delivered(obj):
    """ True if a promise has been delivered """

    return is_proxy_delivered(obj) if is_proxy(obj) \
        else obj.is_delivered()


def deliver(obj):
    """ attempts to deliver a promise """

    return deliver_proxy(obj) if is_proxy(obj) \
        else obj.deliver()


def container(work):
    """ creates a new container promise to find an answer for work """
    return ContainerPromise(work)


def proxy(work):
    """ creates a new proxy promise to find an answer for work """
    return ProxyPromise(work)


class PromiseNotReady(Exception):
    """ Raised when attempting to deliver on a promise whose
    underlying delivery function hasn't been called (see
    container_pair and proxy_pair) """
    pass


class PromiseAlreadyDelivered(Exception):
    """ Raised when a paired promise's delivery function is called
    more than once (see container_pair and proxy_pair) """
    pass


def _settable_promise(promise_type, blocking=False):

    """ This is the 'traditional' type of promise. It's a single-slot,
    write-once value. I like mine better. But check it out, mine can
    turn into the boring one with the greatest of ease! """

    # our shared state! trololol closures
    ptr = list()
    exc = list()
    event = Event() if blocking else None

    # for getting a value to deliver to the promise, or for raising an
    # exception if one was set. This is what will be called by deliver
    def promise_getter():
        if event:
            event.wait()
        if ptr:
            return ptr[0]
        elif exc:
            if event:
                event.clear()
            raise exc[0], exc[1], exc[2]
        else:
            raise PromiseNotReady()

    promise = promise_type(promise_getter)

    # for setting the promise's value.
    def promise_setter(value):
        if ptr:
            raise PromiseAlreadyDelivered()
        else:
            del exc[:]
            ptr[:] = (value,)
            if event:
                event.set()
            deliver(promise)

    # for setting the promise's exception
    def promise_setexc(exc_type, exc_val, exc_tb):
        if ptr:
            raise PromiseAlreadyDelivered()
        else:
            exc[:] = exc_type, exc_val, exc_tb
            if event:
                event.set()

    return (promise, promise_setter, promise_setexc)


def settable_container(blocking=False):

    """ Returns a tuple of a new ContainerPromise, a unary function to
    deliver a value into that promise, and a ternary function to feed
    an exception to the promise.

    eg:
    >>> promise,setter,seterr = settable_container()
    >>> setter(5)
    >>> promise.deliver()
    5

    """

    return _settable_promise(ContainerPromise, blocking=blocking)


def settable_proxy(blocking=False):

    """ Returns a tuple of a new ProxyPromise, a unary function to deliver
    a value into that promise, and a ternary function to feed an
    exception to the promise.

    eg:
    >>> promise,setter,seterr = settable_proxy()
    >>> setter(5)
    >>> promise
    5

    """

    return _settable_promise(ProxyPromise, blocking=blocking)


#
# The end.
