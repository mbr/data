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

.. code-block:: python

    >>> d = I('some data')
    >>> d.read(4)
    u'some'
    >>> d.read(4)
    u' dat'
    >>> d.read(4)
    u'a'
    >>> e = I(u'more data')
    >>> str(e)
    'more data'

Note how ``read`` returns unicode. Additionally, ``readb`` is available:

.. code-block:: python

    >>> f = I(u'I am Ünicode.')
    >>> f.readb()
    'I am \xc3\x9cnicode.'

Every ``data`` object has an encoding attribute which is used for converting
from and to unicode.

.. code-block:: python

    >>> g = I(u'I am Ünicode.', encoding='latin1')
    >>> g.readb()
    'I am \xdcnicode.'

Iteration and line reading are also supported:

.. code-block:: python

    >>> h = I('I am\nof many\nlines')
    >>> h.readline()
    u'I am\n'
    >>> h.readlines()
    [u'of many\n', u'lines']
    >>> i = I('line one\nline two\n')
    >>> list(iter(i))
    [u'line one\n', u'line two\n']


Extras
------

save_to
~~~~~~~

Some useful convenience methods are available:

.. code-block:: python

    >>> j = I('example')
    >>> j.save_to('example.txt')

The ``save_to`` method will use the most efficient way possible to save the
data to a file (``copyfileobj`` or ``write()``). It can also be passed a
file-like object:

.. code-block:: python

    >>> k = I('example2')
    >>> with open('example2.txt', 'wb') as out:
    ...     k.save_to(out)
    ...


temp_saved
~~~~~~~~~~

If you need the output inside a secure temporary file, ``temp_saved`` is
available:

.. code-block:: python

    >>> l = I('goes into tmp')
    >>> with l.temp_saved() as tmp:
    ...     print tmp.name
    ...     print l.read()
    ...
    /tmp/tmpY7nv__
    goes into tmp

``temp_saved`` functions almost identically to ``tempfile.NamedTemporaryFile``,
with one difference: There is no ``delete`` argument. The file is removed only
when the context manager exits.


Python 2 and 3
--------------

``data`` works the same on Python 2 and 3 thanks to `six
<https://pypi.python.org/pypi/six>`_, a few compatibility functions and a
testsuite.

Python 3 is supported from 3.3 onwards, Python 2 from 2.6.
