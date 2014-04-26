Overview of python-promises
===========================

A `Python <http://python.org>`__ module providing container and proxy
promises, supporting delayed linear and multi-processing delivery.

This is dissimilar to
`PEP-3148 <http://www.python.org/dev/peps/pep-3148>`__, where the focus
is on a robust asynchronous delivery framework. We're mostly interested
in simple deferral and most of all, transparent proxies.

At this stage this project is just a rough draft. I've set the version
to 0.9.0 and am not promising any kind of API stability until 1.0.0 at
which point I'll tag it and cut a release. Feel free to play, fork, or
experiment.

-  `python-promises
   documentation <http://obriencj.preoccupied.net/python-promises/>`__
-  `python-promises on
   GitHub <https://github.com/obriencj/python-promises/>`__
-  python-promises not on PyPI until version 1.0.0

Using promises
--------------

*This is very much a work in progress. I am still working out how much I
want to explain, in what order, etc. It may be best to just expect that
everyone knows what a promise is and not explain anything at all... -
Chris*

So let's start simply, assuming that while everyone is already familiar
with the concept of a
`promise <http://en.wiktionary.org/wiki/promise#Noun>`__ and how it
affects them socially, they may not be clear on how the concept relates
to programming and `computer
science <http://en.wikipedia.org/wiki/Futures_and_promises>`__.

It's very likely that you're using something very akin to a promise in
your code, and just not considering it as such. At the most basic level,
one could conceive of a promise as nothing more than say, a memoized
nullary function. One may have thought, "this function involves network
access, so let's not call it unless we absolutely need to load this
data." The placeholder for the value is the promise, as is the code and
any data that would be needed to deliver on it.

There's no free computation involved. To get the value from a promise,
the work still has to be done and delivered. But perhaps it can happen
in another thread or process while you're working on collating ten
thousand similar pieces.

Some languages are built on the concept of the promise and lazy
evaluation. Others offer it as an option, but at the syntax level. And
still others at least provide an OO representation of the concept in
some library. Python doesn't, by default, have any of these.

In this library, the promise isn't necessarily that the passed work will
be executed. The promise being made is that the answer or result of a
piece of computation will be delivered *if asked for*. As such, if no
code ever attempts to retrieve a promised value, it's perfectly
acceptable for there to be no attempt to execute the underlying work.
Put another way, promises are not the same as tasks.

Lazy Container
~~~~~~~~~~~~~~

A lazy container is a simple, object-oriented placeholder. It can be
created by invoking the ``lazy`` function, passing a work function and
any arguments it needs. When delivered, the container will call that
work and collect the result as its answer. Any further invocations of
deliver will return the answer without re-executing the work. However,
if an exception is raised by the work during delivery the container will
not be considered as delivered. In the case of a transient issue (such
as a time-out), delivery can be attempted again until an answer is
finally returned.

::

    >>> from promises import lazy, is_delivered, deliver
    >>> A = lazy(set, [1, 2, 3])
    >>> is_delivered(A)
    False
    >>> print A
    <promises.Container undelivered>
    >>> deliver(A)
    set([1, 2, 3])
    >>> print A
    <promises.Container delivered:set([1, 2, 3])>
    >>> is_delivered(A)
    True

Lazy Proxy
~~~~~~~~~~

Proxies are a way to consume promises without *looking* like you're
consuming promises. You treat the proxy as though it were the answer
itself. A proxy is created by invoking the ``lazy_proxy`` function, and
passing a work function and any arguments it needs. If your work
delivers an int, then treat the proxy like an int. If your work delivers
a dictionary, then treat the proxy like it were a dictionary.

::

    >>> from promises import lazy_proxy, is_delivered, promise_repr
    >>> B = lazy_proxy(set, [1, 2, 3])
    >>> is_delivered(B)
    False
    >>> print promise_repr(B)
    <promises.Proxy undelivered>
    >>> print B
    set([1, 2, 3])
    >>> print promise_repr(B)
    <promises.Proxy delivered:set([1, 2, 3])>
    >>> is_delivered(B)
    True

Proxy Problems
~~~~~~~~~~~~~~

A proxy tries fairly hard to act like the delivered value, by passing
along almost every conceivable call to the underlying answer.

However, proxies are still their own type. As such, any code that is
written which does a type check will potentially misbehave.

An example of this is the builtin
`set <http://docs.python.org/2/library/stdtypes.html#set-types-set-frozenset>`__
type. Below we show that the proxy will happily pass the
`richcompare <http://docs.python.org/2/c-api/typeobj.html#PyTypeObject.tp_richcompare>`__
call along to the underlying set and affirm that A and X are equal.
However, reverse the operands and X will first
`check <http://hg.python.org/cpython/file/779de7b4909b/Objects/setobject.c#l1794>`__
that the arguments to its richcompare call are another set instance.
Since A is not a set (A is an instance of promises.Proxy), X's
richcompare immediately returns False, indicating that X and A are not
equal.

::

    >>> from promises import lazy_proxy, deliver
    >>> A = lazy_proxy(set, [1, 2, 3])
    >>> A
    set([1, 2, 3])
    >>> X = set([1, 2, 3])
    >>> X
    set([1, 2, 3])
    >>> A == X
    True
    >>> X == A
    False
    >>> X == deliver(A)
    True

Broken Promises
~~~~~~~~~~~~~~~

The default behavior of ``deliver`` on a promise will allow any raised
exception to propagate up. This may be undesireable, so there are three
ways to instead gather a ``BrokenPromise`` which will wrap any raised
exception and be returned as the result.

The functions ``breakable`` and ``breakable_proxy`` will create a
container and proxy promise (respectively) for a piece of work. These
functions wrap the work in a try/except clause to catch any exceptions.
A promise created with these functions will be considered delivered but
broken should it raise during delivery, and will not re-attempt
delivery.

As an alternative to creating a breakable promise, the function
``breakable_deliver`` attempts delivery on a promise generated from
``lazy`` or ``lazy_proxy``. If the promise raises during delivery, a
``BrokenPromise`` is generated and returned. However, the promise will
not be considered delivered, and any future attempts at delivery will
cause the work to be executed again.

Requirements
------------

-  `Python <http://python.org>`__ 2.6 or later (no support for Python 3
   unless someone else wants to hack in all the macros for the proxy
   code)

In addition, following tools are used in building, testing, or
generating documentation from the project sources.

-  `Setuptools <http://pythonhosted.org/setuptools/>`__
-  `Coverage.py <http://nedbatchelder.com/code/coverage/>`__
-  `GNU Make <http://www.gnu.org/software/make/>`__
-  `Pandoc <http://johnmacfarlane.net/pandoc/>`__
-  `Sphinx <http://sphinx-doc.org/>`__

These are all available in most linux distributions (eg.
`Fedora <http://fedoraproject.org/>`__), and for OSX via
`MacPorts <http://www.macports.org/>`__.

Building
--------

This module uses `setuptools <http://pythonhosted.org/setuptools/>`__,
so simply run the following to build the project.

.. code:: bash

    python setup.py build

Testing
~~~~~~~

Tests are written as ``unittest`` test cases. If you'd like to run the
tests, simply invoke:

.. code:: bash

    python setup.py test

You may check code coverage via
`coverage.py <http://nedbatchelder.com/code/coverage/>`__, invoked as:

.. code:: bash

    # generates coverage data in .coverage
    coverage run --source=promises setup.py test

    # creates an html report from the above in htmlcov/index.html
    coverage html

I've setup `travis-ci <https://travis-ci.org>`__ and
`coveralls.io <https://coveralls.io>`__ for this project, so tests are
run automatically, and coverage is computed then. Results are available
online:

-  `python-promises on
   Travis-CI <https://travis-ci.org/obriencj/python-promises>`__
-  `python-promises on
   Coveralls.io <https://coveralls.io/r/obriencj/python-promises>`__

Documentation
~~~~~~~~~~~~~

Documentation is built using `Sphinx <http://sphinx-doc.org/>`__.
Invoking the following will produce HTML documentation in the
``docs/_build/html`` directory.

.. code:: bash

    cd docs
    make html

Note that you will need the following installed to successfully build
the documentation:

Documentation is `also available
online <http://obriencj.preoccupied.net/python-promises/>`__.

Related
-------

There are multiple alternative implementations following different
wavelengths of this concept. Here are some for your perusal.

-  `concurrent.futures <http://docs.python.org/dev/library/concurrent.futures.html>`__
   - `Python 3.4 <http://docs.python.org/dev/whatsnew/3.4.html>`__
   includes `PEP-3148 <http://www.python.org/dev/peps/pep-3148>`__
-  `futureutils <https://pypi.python.org/pypi/futureutils>`__ -
   Introduces futures and promises into iterators
-  `aplus <https://github.com/xogeny/aplus>`__ - Promises/A+
   specification in Python
-  `promised <https://code.google.com/p/promised/>`__ - Python "promise"
   for output of asynchronous operations, and callback chaining.

Author
------

Christopher O'Brien obriencj@gmail.com

If this project interests you, you can read about more of my hacks and
ideas on `on my blog <http://obriencj.preoccupied.net>`__.

License
-------

This library is free software; you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this library; if not, see http://www.gnu.org/licenses/.
