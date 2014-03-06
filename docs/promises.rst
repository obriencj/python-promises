Module promises
===============

.. automodule:: promises
  :show-inheritance:

  General
  -------
  .. autofunction:: promises.deliver
  .. autofunction:: promises.is_delivered
  .. autofunction:: promises.is_promise

  .. autoclass:: promises.PromiseAlreadyDelivered
    :show-inheritance:
  .. autoclass:: promises.PromiseNotReady
    :show-inheritance:

  Container Promises
  -------------------
  .. autofunction:: promises.lazy
  .. autofunction:: promises.promise

  Proxy Promises
  --------------
  .. autofunction:: promises.lazy_proxy
  .. autofunction:: promises.promise_proxy
