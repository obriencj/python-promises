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


from multiprocessing.pool import ThreadPool
from promises import promise_proxy
from .multiprocess import ProcessExecutor


__all__ = ( 'ThreadExecutor', 'ProxyThreadExecutor' )


class ThreadExecutor(ProcessExecutor):
    """
    A way to provide multiple promises which will be delivered in a
    separate threads
    """

    def _get_pool(self):
        if not self._pool:
            self._pool = ThreadPool(processes=self._processes)
        return self._pool


class ProxyThreadExecutor(ThreadExecutor):
    """
    Creates transparent proxy promises, which will deliver in a
    separate thread
    """

    def _promise(self):
        return promise_proxy(blocking=True)


#
# The end.
