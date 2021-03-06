
# Overview of python-promises

[![Build Status](https://travis-ci.org/obriencj/python-promises.png?branch=master)](https://travis-ci.org/obriencj/python-promises)
[![Coverage Status](https://coveralls.io/repos/obriencj/python-promises/badge.png?branch=master)](https://coveralls.io/r/obriencj/python-promises?branch=master)

A [Python] module providing container and proxy promises, supporting
delayed linear and multi-processing delivery.

This is dissimilar to [PEP-3148], where the focus is on a robust
asynchronous delivery framework. We're mostly interested in simple
deferral and most of all, transparent proxies.

At this stage this project is just a rough draft. I've set the version
to 0.9.0 and am not promising any kind of API stability until 1.0.0 at
which point I'll tag it and cut a release. Feel free to play, fork, or
experiment.

* [python-promises documentation][docs]
* [python-promises on GitHub][github]
* python-promises not on PyPI until version 1.0.0

[python]: http://python.org "Python"

[pep-3148]: http://www.python.org/dev/peps/pep-3148
"PEP-3148 - futures - execute computations asynchronously"

[docs]: http://obriencj.preoccupied.net/python-promises/

[github]: https://github.com/obriencj/python-promises/
"python-promises on GitHub"


## Using promises

*This is very much a work in progress. I am still working out how much
 I want to explain, in what order, etc. It may be best to just expect
 that everyone knows what a promise is and not explain anything at
 all... - Chris*

So let's start simply, assuming that while everyone is already
familiar with the concept of a [promise][promise-noun] and how it
affects them socially, they may not be clear on how the concept
relates to programming and [computer science][cs-promise].

It's very likely that you're using something very akin to a promise in
your code, and just not considering it as such. At the most basic
level, one could conceive of a promise as nothing more than say, a
memoized nullary function. One may have thought, "this function
involves network access, so let's not call it unless we absolutely
need to load this data." The placeholder for the value is the promise,
as is the code and any data that would be needed to deliver on it.

There's no free computation involved. To get the value from a promise,
the work still has to be done and delivered. But perhaps it can happen
in another thread or process while you're working on collating ten
thousand similar pieces.

Some languages are built on the concept of the promise and lazy
evaluation. Others offer it as an option, but at the syntax level. And
still others at least provide an OO representation of the concept in
some library. Python doesn't, by default, have any of these.

In this library, the promise isn't necessarily that the passed work
will be executed. The promise being made is that the answer or result
of a piece of computation will be delivered *if asked for*. As such,
if no code ever attempts to retrieve a promised value, it's perfectly
acceptable for there to be no attempt to execute the underlying
work. Put another way, promises are not the same as tasks.

[promise-noun]: http://en.wiktionary.org/wiki/promise#Noun

[cs-promise]: http://en.wikipedia.org/wiki/Futures_and_promises
"Futures and Promises"


### Lazy Container

A lazy container is a simple, object-oriented placeholder. It can be
created by invoking the `lazy` function, passing a work function and
any arguments it needs. When delivered, the container will call that
work and collect the result as its answer. Any further invocations of
deliver will return the answer without re-executing the work. However,
if an exception is raised by the work during delivery the container
will not be considered as delivered. In the case of a transient issue
(such as a time-out), delivery can be attempted again until an answer
is finally returned.

```
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
```


### Lazy Proxy

Proxies are a way to consume promises without *looking* like you're
consuming promises. You treat the proxy as though it were the answer
itself. A proxy is created by invoking the `lazy_proxy` function, and
passing a work function and any arguments it needs. If your work
delivers an int, then treat the proxy like an int. If your work
delivers a dictionary, then treat the proxy like it were a dictionary.

```
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
```


### Proxy Problems

A proxy tries fairly hard to act like the delivered value, by passing
along almost every conceivable call to the underlying answer.

However, proxies are still their own type. As such, any code
that is written which does a type check will potentially misbehave.

An example of this is the builtin [set] type. Below we show that the
proxy will happily pass the [richcompare] call along to the underlying
set and affirm that A and X are equal. However, reverse the operands
and X will first [check][set_richcompare] that the arguments to its
richcompare call are another set instance. Since A is not a set (A is
an instance of promises.Proxy), X's richcompare immediately returns
False, indicating that X and A are not equal.

```
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
```

[set]: http://docs.python.org/2/library/stdtypes.html#set-types-set-frozenset
"5.7. Set Types - set, frozenset"

[richcompare]: http://docs.python.org/2/c-api/typeobj.html#PyTypeObject.tp_richcompare

[set_richcompare]: http://hg.python.org/cpython/file/779de7b4909b/Objects/setobject.c#l1794


### Broken Promises

The default behavior of `deliver` on a promise will allow any raised
exception to propagate up. This may be undesireable, so there are
three ways to instead gather a `BrokenPromise` which will wrap any
raised exception and be returned as the result.

The functions `breakable` and `breakable_proxy` will create a
container and proxy promise (respectively) for a piece of work. These
functions wrap the work in a try/except clause to catch any
exceptions. A promise created with these functions will be considered
delivered but broken should it raise during delivery, and will not
re-attempt delivery.

As an alternative to creating a breakable promise, the function
`breakable_deliver` attempts delivery on a promise generated from
`lazy` or `lazy_proxy`. If the promise raises during delivery, a
`BrokenPromise` is generated and returned. However, the promise will
not be considered delivered, and any future attempts at delivery will
cause the work to be executed again.


## Requirements

* [Python] 2.6 or later (no support for Python 3 unless someone else
  wants to hack in all the macros for the proxy code)

In addition, following tools are used in building, testing, or
generating documentation from the project sources.

* [Setuptools]
* [Coverage.py]
* [GNU Make]
* [Pandoc]
* [Sphinx]

These are all available in most linux distributions (eg. [Fedora]), and
for OSX via [MacPorts].

[setuptools]: http://pythonhosted.org/setuptools/

[coverage.py]: http://nedbatchelder.com/code/coverage/

[gnu make]: http://www.gnu.org/software/make/

[pandoc]: http://johnmacfarlane.net/pandoc/

[sphinx]: http://sphinx-doc.org/

[fedora]: http://fedoraproject.org/

[macports]: http://www.macports.org/


## Building

This module uses [setuptools], so simply run the following to build
the project.

```bash
python setup.py build
```


### Testing

Tests are written as `unittest` test cases. If you'd like to run the
tests, simply invoke:

```bash
python setup.py test
```

You may check code coverage via [coverage.py], invoked as:

```bash
# generates coverage data in .coverage
coverage run --source=promises setup.py test

# creates an html report from the above in htmlcov/index.html
coverage html
```

I've setup [travis-ci] and [coveralls.io] for this project, so tests
are run automatically, and coverage is computed then. Results are
available online:

* [python-promises on Travis-CI][promises-travis]
* [python-promises on Coveralls.io][promises-coveralls]

[travis-ci]: https://travis-ci.org

[coveralls.io]: https://coveralls.io

[promises-travis]: https://travis-ci.org/obriencj/python-promises

[promises-coveralls]: https://coveralls.io/r/obriencj/python-promises


### Documentation

Documentation is built using [Sphinx]. Invoking the following will
produce HTML documentation in the `docs/_build/html` directory.

```bash
cd docs
make html
```

Note that you will need the following installed to successfully build
the documentation:

Documentation is [also available online][docs].


## Related

There are multiple alternative implementations following different
wavelengths of this concept. Here are some for your perusal.

* [concurrent.futures] - [Python 3.4] includes [PEP-3148]
* [futureutils] - Introduces futures and promises into iterators
* [aplus] - Promises/A+ specification in Python
* [promised] - Python "promise" for output of asynchronous operations,
  and callback chaining.

[concurrent.futures]: http://docs.python.org/dev/library/concurrent.futures.html
[futureutils]: https://pypi.python.org/pypi/futureutils
[aplus]: https://github.com/xogeny/aplus
[promised]: https://code.google.com/p/promised/
[python 3.4]: http://docs.python.org/dev/whatsnew/3.4.html


## Author

Christopher O'Brien  <obriencj@gmail.com>

If this project interests you, you can read about more of my hacks and
ideas on [on my blog](http://obriencj.preoccupied.net).


## License

This library is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 3 of the
License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, see
<http://www.gnu.org/licenses/>.
