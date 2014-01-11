
# Overview of python-promises

A [Python] module providing container and proxy promises, supporting
delayed linear and multi-processing delivery.

This is dissimilar to [PEP-3148], where the focus is on simplified
parallel execution. We focus more on the concept of a promise as a
placeholder to a value which may not have been delivered yet. Futures
as described could be used to deliver on promises, perhaps.

At this stage this project is just a rough draft. I've set the version
to 0.9.0 and am not promising any kind of API stability until 1.0.0 at
which point I'll tag it and cut a release. Feel free to play, fork, or
experiment.

* [python-promises on GitHub][github]
* python-promises not on PyPI until version 1.0.0

[python]: http://python.org "Python"

[pep-3148]: http://www.python.org/dev/peps/pep-3148
"PEP-3148 - futures - execute computations asynchronously"

[github]: https://github.com/obriencj/python-promises/
"python-promises on GitHub"


## These Python Promises

*This is very much a work in progress. I am still working out how much
 I want to explain, in what order, etc.*

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


## Container Promise

A container promise is a simple, object-oriented placeholder. When
created it is handed a work function, which can be any nullary
callable. When delivered, the promise will call that work and collect
the result as its answer. Any further invocations of deliver will
return the answer without re-executing the work. However, if an
exception is raised by the work during delivery the promise will not
be considered as delivered. In the case of a transient issue (such as
a time-out), delivery can be attempted again until an answer is
finally returned.

More: [Example Container Promise]

[Example Container Promise]: https://github.com/obriencj/python-promises/wiki/Example-Container-Promise


## Proxy Promise

Proxy promises are a way to write promises without *looking* like
you're writing promises. You treat the promise as though it were the
answer itself. If your work delivers an int, then treat the proxy like
an int. If your work delivers a dictionary, then treat the proxy like
it were a dictionary.

More: [Example Proxy Promise]

A proxy promise tries fairly hard to act like the delivered value, by
passing along almost every conceivable call to the underlying answer.

However, proxy promises are still their own type. As such, any code
that is written which does a type check will potentially misbehave.

An example of this is the builtin [set] type. Below we show that the
proxy will happily pass the [richcompare] call along to the underlying
set and affirm that A and X are equal. However, reverse the operands
and X will first [check][set_richcompare] that the arguments to its
richcompare call are another set instance. Since A is not a set (A is
an instance of ProxyPromise), X's richcompare immediately returns
False, indicating that X and A are not equal.

```
>>> from promises import proxy, deliver
>>> A = proxy(lambda: set([1, 2, 3]))
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

[Example Proxy Promise]: https://github.com/obriencj/python-promises/wiki/Example-Proxy-Promise

[set]: http://docs.python.org/2/library/stdtypes.html#set-types-set-frozenset
"5.7. Set Types - set, frozenset"

[richcompare]: http://docs.python.org/2/c-api/typeobj.html#PyTypeObject.tp_richcompare

[set_richcompare]: http://hg.python.org/cpython/file/779de7b4909b/Objects/setobject.c#l1794


## Requirements

* [Python] 2.6 or later (no support for Python 3 unless someone else
  wants to hack in all the macros for the proxy code)


## Install

This module uses setuptools, so simply run

```
python setup.py install
```


## Contact

Christopher O'Brien <obriencj@gmail.com>


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

