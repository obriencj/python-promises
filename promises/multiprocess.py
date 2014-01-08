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

Multi-process Promises for Python

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3

"""


from abc import ABCMeta, abstractmethod
from multiprocessing.pool import Pool
from promises import ContainerPromise, ProxyPromise


class Promising(object):
    
    """ A way to provide multiple promises which will be delivered in
    a separate process. See ContainerPromising or ProxyPromising for
    concrete implementations. """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __promise__(self, work):
        """ must be overridden to provide a promise to do the
        specified work """
        return None

    def __init__(self, processes=None):
        self.__processes = processes
        self.__pool = None
        
    def __enter__(self):
        """ Though Promising offers the management interface, it
        doesn't really use it in any way. I consider it a beneficial
        marker that we're operating against multiple processes though."""
        return self

    def __exit__(self, exc_type, _exc_val, _exc_tb):
        return (exc_type is None)

    def promise(self, work):
        """ queue up work as a promise, which may be delievered in a
        separate process. """

        if not self.__pool:
            self.__pool = Pool(processes=self.__processes)
        
        # yay for Pool.apply_async, doing all the heavy lifting for
        # us, so we don't need to correlate tasks or deal with Queues
        # ourselves. However, this does NOT handle KeyboardInterrupt
        # well at all... I may need to look at catching that myself.
        result = self.__pool.apply_async(work, [], {})
        return self.__promise__(result.get)

    def terminate(self):
        """ breaks all the remaining undelivered promises """
        self.__pool.terminate()
        self.__pool = None

    def deliver(self):
        """ blocks until all underlying promises have been delivered """
        self.__pool.close()
        self.__pool = None

    def is_delivered(self):
        # TODO better to ask if the pool is empty, check on this
        # later.
        return (self.__pool is None)


class ContainerPromising(Promising):

    """ Creates container promises, which will deliver in a separate
    process """

    def __promise__(self, work):
        return ContainerPromise(work)


class ProxyPromising(Promising):

    """ Creates transparent proxy promises, which will deliver in a
    separate process """

    def __promise__(self, work):
        return ProxyPromise(work)


#
# The end.
