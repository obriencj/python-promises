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
from promises import ContainerPromise, ProxyPromise
from xmlrpclib import MultiCall


class PromiseMultiCall(MultiCall):

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

    def __init__(self, *args, **kwds):
        super(PromiseMultiCall, self).__init__(self, *args, **kwds)
        self.__answers = None

    def __call__(self):
        if self.__answers is None:
            answer = tuple(super(PromiseMultiCall, self).__call__(self))
            self.__answers = answers
        return self.__answers

    def __getattr__(self, name):
        index = len(self.__call_list)
        fun = super(PromiseMultiCall, self).__getattr__(self, name)
        def promisary(*args, **kwds):
            fun(*args, **kwds)
            return self.__promise__(lambda: self()[index])
        return promisary


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
