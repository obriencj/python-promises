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

XML RPC MultiCall Promises

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3

"""


from functools import partial
from promises import lazy, lazy_proxy
from xmlrpclib import MultiCall


__all__ = ( 'LazyMultiCall', 'ProxyMultiCall' )


class LazyMultiCall(object):

    """ A wrapper to xmlrpclib.MultiCall which allows the programmer
    to receive promises for the calls as they are written, rather than
    having to gather and distribute the results at the end. Forcing a
    promise to deliver will also force this MultiCall to execute all
    of its queued xmlrpc calls."""


    def __promise__(self, work):
        return lazy(work)


    def __init__(self, server, group_calls=0):
        """ server is an xmlrpclib.Server instance. If group_calls is
        greater than zero, it is the upper limit on how many promises
        will be delivered at a time. """

        self.__server = server
        self.__mclist = list()
        self.__mc = None
        self.__counter = 0

        group_calls = int(group_calls)
        self.__group_calls = group_calls if group_calls > 0 else 0


    def __enter__(self):
        return self


    def __exit__(self, exc_type, _exc_val, _exc_tb):
        self()
        return (exc_type is None)


    def __call__(self):
        """ Retrieve answers for any of our currently outstanding
        promises. """

        for mc in self.__mclist:
            mc()


    def __getattr__(self, name):
        def promisary(*args, **kwds):
            # make sure we have an underlying memoized multicall
            multicall = self.__get_multicall()

            # enqueue the call in the multicall
            getattr(multicall, name)(*args, **kwds)

            # this is how we'll relate back to our answers from the
            # current multicall.
            index = self.__counter
            self.__counter += 1

            # promise to get the answer out of this exact multicall's
            # collection of answers
            work = partial(self.__deliver_on, multicall, index)

            # the resulting promise will keep a reference to the
            # particular memoized multicall, as that is where it will
            # want to get its answer from.
            promised = self.__promise__(work)

            # if this promise puts us at our threhold for grouping
            # calls, then it's time to start using a new mc
            if self.__group_calls and self.__group_calls <= self.__counter:
                self.__mc = None
                self.__counter = 0

            return promised

        promisary.func_name = name
        return promisary


    def __get_multicall(self):
        multicall = self.__mc
        if multicall is None:
            multicall = MemoizedMultiCall(self.__server)
            self.__mclist.append(multicall)
            self.__mc = multicall
            self.__counter = 0

        return multicall


    def __deliver_on(self, mc, index):
        assert(mc is not None)

        # if the promise is against the current MC, then we need to
        # deliver on it and clear ourselves to create a new
        # one. Otherwise, use the memoized answers for the already
        # delivered MC. Then we return the result at the given index.
        if mc is self.__mc:
            self.__mc = None
            self.__counter = 0

        # a great feature of this is that the delivery or access of
        # the promise will also raise the underlying fault if there
        # happened to be one
        return mc()[index]


def ProxyMultiCall(LazyMultiCall):

    """ A PromiseMultiCall which will returns Proxy instead of Container """

    def __promise__(self, work):
        return lazy_proxy(work)


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


#
# The end.
