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


from functools import partial
from multiprocessing.pool import Pool
from promises import lazy, lazy_proxy


__all__ = ( 'Executor', 'ProxyExecutor' )


class Executor(object):
    
    """ A way to provide multiple promises which will be delivered in
    a separate process. """

    def __promise__(self, work):
        """ must be overridden to provide a promise to do the
        specified work """
        return lazy(work)

    def __init__(self, processes=None):
        self.__processes = processes
        self.__pool = None
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, _exc_val, _exc_tb):
        self.deliver()
        return (exc_type is None)

    def future(self, work, *args, **kwds):
        """ queue up work as to occur in a separate process, returning
        a container to reference the result """

        if not self.__pool:
            self.__pool = Pool(processes=self.__processes)
        
        if args or kwds:
            work = partial(work, *args, **kwds)

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


class ProxyExecutor(Executor):

    """ Creates transparent proxy promises, which will deliver in a
    separate process """

    def __promise__(self, work):
        return lazy_proxy(work)


#
# The end.
