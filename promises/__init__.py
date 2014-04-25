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

:author: Christopher O'Brien  <obriencj@gmail.com>
:license: LGPL v.3
"""


from _proxy import Proxy
from _proxy import is_proxy, is_proxy_delivered, deliver_proxy
from functools import partial
from sys import exc_info
from threading import Event


__all__ = ( 'Container', 'Proxy', 'BrokenPromise',
            'lazy', 'lazy_proxy',
            'promise', 'promise_proxy',
            'breakable', 'breakable_proxy',
            'breakable_deliver',
            'PromiseNotReady', 'PromiseAlreadyDelivered',
            'is_promise', 'is_delivered', 'deliver',
            'promise_repr', )


class Container(object):
    """
    Simple promise mechanism. Acts as a container to the promised work
    until delivered, and there-after acts as a container to the return
    value from executing the work. Will invoke the promised work
    function exactly once, but can deliver the answer multiple times.
    """

    __slots__ = ('_work', '_answer')


    def __init__(self, work):
        """
        promises to provide the answer from calling work. work must be
        either a nullary (zero-argument) callable, or a non-callable
        value. If work is non-callable, then this promise is
        considered immediately delivered, and the work value becomes
        the answer.
        """

        if callable(work):
            # TODO: check work arity. Must be nullary.
            self._work = work
            self._answer = None
        else:
            self._work = None
            self._answer = work


    def __del__(self):
        self._work = None
        self._answer = None


    def is_delivered(self):
        """
        True if the promised work has been called and an answer has been
        recorded.
        """

        return self._work is None


    def deliver(self):
        """
        Deliver on promised work. Will only execute the work if an answer
        has not already been found. If an exception is raised during
        the execution of work, it will be cascade up from here as
        well. Returns the answer to the work once known.
        """

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


    def __repr__(self):
        answer = self._answer
        if answer is None:
            return "<promises.Container undelivered>"
        elif isinstance(answer, BrokenPromise):
            return "<promises.Container broken>"
        else:
            return "<promises.Container delivered>"


def is_promise(obj):
    """
    True if `obj` is a promise (either a proxy or a container)
    """

    return (is_proxy(obj) or \
                (hasattr(obj, "is_delivered") and
                 hasattr(obj, "deliver")))


def is_delivered(a_promise):
    """
    True if `a_promise` is a promise and has been delivered
    """

    return is_proxy_delivered(a_promise) if is_proxy(a_promise) \
        else a_promise.is_delivered()


def deliver(on_promise):
    """
    Attempts to deliver on a promise, and returns the resulting
    value. If the delivery of work causes an exception, it will be
    raised here.

    Parameters
    ----------
    on_promise : `Proxy` or `Container` promise
      the promise to deliver on

    Returns
    -------
    value
      the promised work if it could be successfully computed
    """

    return deliver_proxy(on_promise) if is_proxy(on_promise) \
        else on_promise.deliver()


def lazy(work, *args, **kwds):
    """
    Creates a new container promise to find an answer for `work`.

    Parameters
    ----------
    work : `callable`
      executed when the promise is delivered
    *args
      optional arguments to pass to work
    **kwds
      optional keyword arguments to pass to work

    Returns
    -------
    promise : `Container`
      the container promise which will deliver on `work(*args, **kwds)`
    """

    if args or kwds:
        work = partial(work, *args, **kwds)
    return Container(work)


def lazy_proxy(work, *args, **kwds):
    """
    Creates a new proxy promise to find an answer for `work`.

    Parameters
    ----------
    work : `callable`
      executed when the promise is delivered
    *args
      optional arguments to pass to work
    **kwds
      optional keyword arguments to pass to work

    Returns
    -------
    promise : `Proxy`
      the proxy promise which will deliver on `work(*args, **kwds)`
    """

    if args or kwds:
        work = partial(work, *args, **kwds)
    return Proxy(work)


class PromiseNotReady(Exception):
    """
    Raised when attempting to deliver on a promise whose underlying
    delivery function hasn't been called.
    """

    pass


class PromiseAlreadyDelivered(Exception):
    """
    Raised when a paired promise's delivery function is called more
    than once.
    """

    pass


def _promise(promise_type, blocking=False):
    """
    This is the 'traditional' type of promise. It's a single-slot,
    write-once value.
    """

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
    def promise_seterr(exc_type, exc_val, exc_tb):
        if ptr:
            raise PromiseAlreadyDelivered()
        else:
            exc[:] = exc_type, exc_val, exc_tb
            if event:
                event.set()

    return (promise, promise_setter, promise_seterr)


def promise(blocking=False):
    """
    Returns a tuple of a new Container, a unary function to deliver a
    value into that promise, and a ternary function to feed an
    exception to the promise.

    If `blocking` is True, then any attempt to deliver on the promise
    will block until/unless a value or exception has been set via the
    setter or seterr functions.

    Returns
    -------
    promise : `Container`
      promise acting as a placeholder for future data
    setter : `function(value)`
      function which delivers a value to fulfill the promise
    seterr : `function(exc_type, exc_inst, exc_tb)`
      function which delivers exc_info to raise on delivery of the promise

    Examples
    --------
    >>> prom, setter, seterr = promise()
    >>> setter(5)
    >>> deliver(prom)
    5
    """

    return _promise(Container, blocking=blocking)


def promise_proxy(blocking=False):
    """
    Returns a tuple of a new Proxy, a unary function to deliver a
    value into that promise, and a ternary function to feed an
    exception to the promise.

    If `blocking` is True, then any attempt to deliver on the promise
    (including accessing its members) will block until/unless a value
    or exception has been set via the setter or seterr functions.

    Returns
    -------
    promise : `Proxy`
      promise acting as a placeholder for future data
    setter : `function(value)`
      function which delivers a value to fulfill the promise
    seterr : `function(exc_type, exc_inst, exc_tb)`
      function which delivers exc_info to raise on delivery of the promise

    Examples
    --------
    >>> prom, setter, seterr = promise_proxy()
    >>> setter(5)
    >>> prom
    5
    """

    return _promise(Proxy, blocking=blocking)


class BrokenPromise(object):
    """
    Result indicating a promise was broken. See the `breakable_lazy`,
    `breakable_proxy`, and `breakable_deliver` functions for more
    information.
    """

    def __init__(self, reason=None):
        self.reason = reason
        # self._retry = retry


    # def retry(self):
    #     """
    #     If this broken promise was created with a callable retry value,
    #     attempts to call and returns the result. If retry was
    #     specified but was non-callable, returns retry. If retry was
    #     not specified, or was None, returns self (the BrokenPromise
    #     instance).
    #     """
    #
    #     ret = self._retry
    #     if ret is None:
    #         return self
    #     elif callable(ret):
    #         return ret()
    #     else:
    #         return ret


def _breakable_work(work, *args, **kwds):
    try:
        result = work(*args, **kwds)
    except Exception as ex:
        #retry = partial(work, *args, **kwds)
        #result = BrokenPromise(reason=exc_info(), retry=retry)
        result = BrokenPromise(reason=exc_info())
    return result


def breakable(work, *args, **kwds):
    """
    Creates a container promise to perform work. If delivery of the
    work raises an Exception, a BrokenPromise instance is created to
    wrap the exc_info and is returned in lieu of a result.

    Unlike the normal promise created by `lazy_proxy`, raising an
    Exception in the work will result in the promise being considered
    delivered, but broken. Further attempts at delivery will not
    re-execute the work, but will return the BrokenPromise instance
    from the first failure.
    """

    return lazy(_breakable_work, work, *args, **kwds)


def breakable_proxy(work, *args, **kwds):
    """
    Creates a proxy promise to perform work. If delivery of the work
    raises an Exception, a BrokenPromise instance is created to wrap
    the exc_info and is returned in lieu of a result.

    Unlike the normal promise created by `lazy`, raising an Exception
    in the work will result in the promise being considered delivered,
    but broken. Further attempts at delivery will not re-execute the
    work, but will return the BrokenPromise instance from the first
    failure.
    """

    return lazy_proxy(_breakable_work, work, *args, **kwds)


def breakable_deliver(on_promise):
    """
    Attempts to deliver on a promise. If delivery raises an Exception,
    it is caught and the exc_info is stored into a BrokenPromise
    instance which is returned in lieu of a normal result.

    Note that this can be called on any lazy or container promise, not
    just those that were created as breakable via the `breakable_lazy`
    and `breakable_proxy` functions.

    Using this function to deliver on a promise will not change the
    behavior of whether it is considered delivered or not when an
    Exception is raised.
    """

    try:
        result = deliver(on_promise)
    except Exception as ex:
        result = BrokenPromise(reason=exc_info())
    return result


def promise_repr(p):
    """
    Representation of a promise. If the promise is undelivered, will
    not deliver on it. If it is delivered, will deliver to check if
    the delivery indicates that the promise was broken.
    """

    if not is_proxy(p):
        # non-promises and container promises just get a normal repr
        return repr(p)

    elif not is_delivered(p):
        return "<promises.Proxy undelivered>"

    elif isinstance(breakable_deliver(p), BrokenPromise):
        return "<promises.Proxy broken>"

    else:
        return "<promises.Proxy delivered>"


#
# The end.
