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

XML RPC Multical Promises

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3

"""


from abc import ABCMeta, abstractmethod
from functools import partial
from promises import ContainerPromise, ProxyPromise
from xmlrpclib import MultiCall


class PromiseMultiCall(object):

    """ An alternative to xmlrpclib.MultiCall which allows the
    programmer to receive promises for the calls as they are written,
    rather than having to gather and distribute the results at the
    end. Forcing a promise to deliver will also force this MultiCall
    to execute all of its queued xmlrpc calls. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __promise__(self, work):
        """ must be overridden to provide a promise to do the
        specified work """
        return None

    def __init__(self, server):
        self.server = server
        self.__mc = None
        self.__counter = 0

    def __enter__(self):
        """ The managed interface handler for this is just fluff, so
        that you can choose to use the 'with' keyword to denote when
        you're using the multicall """
        return self

    def __exit__(self, exc_type, _exc_val, _exc_tb):
        return (exc_type is None)

    def deliver(self):
        if self.__mc is not None:
            self.__mc()
            self.__mc  = None
            self.__counter = 0

    def __deliver_on(self, mc, index):
        # if the promise is against the current MC, then we need to
        # deliver on it and clear ourselves to create a new
        # one. Otherwise, use the memoized answers for the already
        # delivered MC. Then we return the result at the given index.
        if mc is self.__mc:
            self.deliver()

        # a great feature of this is that the delivery or access of
        # the promise will also raise the underlying fault if there
        # happened to be one
        return mc.deliver()[index]

    def __getattr__(self, name):
        def promisary(*args, **kwds):
            # make sure we have an underlying memoized multicall
            multicall = self.__mc
            if multicall is None:
                multicall = MemoizedMultiCall(self.server)
                self.__mc = multicall

            # enqueue the call in the multicall
            getattr(multicall, name)(*args, **kwds)

            # this is how we'll relate back to our answers from the
            # current multicall. We wait to capture and increment this
            # value until we're certain that we've been used.
            index = self.__counter
            self.__counter += 1
            
            # promise to get the answer out of this exact multicall's
            # collection of answers
            work = partial(self.__deliver_on, multicall, index)

            # the resulting promise will keep a reference to the
            # particular memoized multicall, as that is where it will
            # want to get its answer from.
            return self.__promise__(work)

        promisary.func_name = name
        return promisary


class MemoizedMultiCall(MultiCall):
    """ A Memoized MultiCall, will only perform the underlying xmlrpc
    call once, remembers the answers for all further requests """

    def __init__(self, server):
        MultiCall.__init__(self, server)
        self.__answers = None

    def __call__(self):
        if self.__answers is None:
            self.__answers = MultiCall.__call__(self)
        return self.__answers


def ProxyMultiCall(PromiseMultiCall):
    """ A MultiCall which will return ProxyPromises """

    def __promise__(self, work):
        return ProxyPromise(work)


def ContainerMultiCall(PromiseMultiCall):
    """ A MultiCall which will return ContainerPromises """

    def __promise__(self, work):
        return ContainerPromise(work)


#
# The end.
