data
====

``data`` is a small Python module that allows you to treat input in a singular
way and leave it up to the caller to supply a byte-string, a unicode object, a
file-like or a filename.

.. code-block:: python

    >>> from data import Data as I
    >>> a = I(u'hello, world')
    >>> open('helloworld.txt', 'w').write('hello, world from a file')
    >>> b = I(file='helloworld.txt')
    >>> c = I(open('helloworld.txt'))
    >>> print unicode(a)
    hello, world
    >>> print unicode(b)
    hello, world from a file
    >>> print unicode(c)
    hello, world from a file
    >>>


Fitting in
----------

All instances support methods like ``read`` or ``__str__`` that make it easy to
fit it into existing APIs:




Python 2 and 3
--------------

``data`` works the same on Python 2 and 3 thanks to `six
<https://pypi.python.org/pypi/six>`_, a few compatibility functions and a
testsuite.

Python 3 is supported from 3.3 onwards, Python 2 from 2.6.
