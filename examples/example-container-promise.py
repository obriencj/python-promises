#! /usr/bin/env python2

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
author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3
"""


# Let's start out with showing simple container promises. A container
# promise is a placeholder for the answer to a piece of work. The
# piece of work is a nullary (zero-argument) callable. When the
# deliver function is called on the promise, it evaluates its
# underlying work, remembers the result, and discards the work object
# (so it can be GC'd). From that point onward, further deliver calls
# on that promise will return the already solved answer.


from promises import container, deliver, is_delivered
from functools import partial


def do_hard_work(value):
    print "Working hard on %r" % value
    return value * 2


# create promises to do some very hard work on the values 0-9
todo = [container(partial(do_hard_work, i)) for i in xrange(0, 10)]


# let's go through all the odd indexed promises and deliver on them
for index,promised in enumerate(todo):
    if index & 1:
        print "promised %r: is_delivered? %r" % (index, is_delivered(promised))
        print "promised %r: deliver -> %r" % (index, deliver(promised))


# now we'll look through all of our promises again and deliver on all
# of them. The odd indexed ones have already been delivered upon, so
# they don't repeat their hard work.
for index,promised in enumerate(todo):
    print "promised %r: is_delivered? %r" % (index, is_delivered(promised))
    print "promised %r: deliver -> %r" % (index, deliver(promised))

#
# The end.
