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

:author: Christopher O'Brien  <obriencj@gmail.com>
:license: LGPL v.3
"""


from . import promise, promise_proxy
from multiprocessing.pool import Pool


__all__ = ('ProcessExecutor', 'ProxyProcessExecutor')


def _perform_work(*args, **kwds):
    """
    This function is what the worker processes will use to collect the
    result from work (whether via return or raise)

    Returns
    -------
    value : `tuple`
      `(True, result)` if `work()` succeeds, else `(False, exc_info)`
      if an exception was raised
    """

    work, args = args

    try:
        return (True, work(*args, **kwds))
    except Exception as exc:
        # we are discarding the stack trace as it won't survive
        # pickling (which is how it will be passed back to the
        # handler from the worker process/thread)
        return (False, (type(exc), exc, None))


class ProcessExecutor(object):
    """
    Create promises which will deliver in a separate process.
    """

    def __init__(self, processes=None):
        self._processes = processes
        self._pool = None


    def __enter__(self):
        return self


    def __exit__(self, exc_type, _exc_val, _exc_tb):
        """
        Using the managed interface forces blocking delivery at the end of
        the managed segment.
        """

        self.deliver()
        return (exc_type is None)


    def _promise(self):
        """
        override to use a different promise mechanism
        """

        return promise(blocking=True)


    def _get_pool(self):
        """
        override to provide a different pool implementation
        """

        if not self._pool:
            self._pool = Pool(processes=self._processes)
        return self._pool


    def future(self, work, *args, **kwds):
        """
        Promise to deliver on the results of work in the future.

        Parameters
        ----------
        work : `callable`
          This is the work which will be performed to deliver on the
          future.
        *args : `optional positional parameters`
          arguments to the `work` function
        **kwds : `optional named parameters`
          keyword arguments to the `work` function

        Returns
        -------
        value : `promise`
          a promise acting as a placeholder for the result of
          evaluating `work(*args, **kwds)`. Note that calling `deliver`
          on this promise will potentially block until the underlying
          result is available.
        """

        promised, setter, seterr = self._promise()

        def callback(value):
            # value is collected as the result of the _perform_work
            # function at the top of this module
            success, result = value
            if success:
                setter(result)
            else:
                seterr(*result)

        # queue up the work in our pool
        pool = self._get_pool()
        pool.apply_async(_perform_work, [work, args], kwds, callback)

        return promised


    def terminate(self):
        """
        Breaks all the remaining undelivered promises, halts execution of
        any parallel work being performed.

        Any promise which had not managed to be delivered will never
        be delivered after calling `terminate`. Attempting to call
        `deliver` on them will result in a deadlock.
        """

        # TODO: is there a way for us to cause all undelivered
        # promises to raise an exception of some sort when this
        # happens? That would be better than deadlocking while waiting
        # for delivery.

        if self._pool is not None:
            self._pool.terminate()
            self._pool = None


    def deliver(self):
        """
        Deliver on all underlying promises. Blocks until complete.
        """

        if self._pool is not None:
            self._pool.close()
            self._pool.join()
            self._pool = None


class ProxyProcessExecutor(ProcessExecutor):
    """
    Create transparent proxy promises which will deliver in a separate
    process.
    """

    def _promise(self):
        return promise_proxy(blocking=True)


#
# The end.
