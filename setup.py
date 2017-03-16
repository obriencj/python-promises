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
Promises for Python

Yet another module for doing promises in python! This time with
transparent proxies, and other convoluted stuff that will make you
wish someone smarter had worked on this.

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL v.3
"""


from setuptools import setup, Extension
import multiprocessing  # NOQA : tests needs this to be imported


ext = [Extension("promises._proxy", ["promises/proxy.c"]), ]


setup(name = "promises",
      version = "0.9.0",

      packages = ["promises", ],

      ext_modules = ext,

      test_suite = "tests",

      # PyPI information
      author = "Christopher O'Brien",
      author_email = "obriencj@gmail.com",
      url = "https://github.com/obriencj/python-promises",
      license = "GNU Lesser General Public License",

      description = "Promises, container and transparent, with"
      " threading and multiprocessing support",

      provides = ["promises", ],
      requires = [],
      platforms = ["python2 >= 2.6", ],

      classifiers = [
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 2",
          "Topic :: Software Development", ])


#
# The end.
