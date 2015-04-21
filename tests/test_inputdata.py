# coding: utf-8

from contextlib import contextmanager
from functools import partial
import os
import tempfile

from six import text_type, binary_type, PY2, reraise, StringIO
import pytest

from data import Data as I


@contextmanager
def tmpfn(*args, **kwargs):
    try:
        fd, fn = tempfile.mkstemp()
        os.close(fd)
        yield fn
    finally:
        try:
            os.unlink(fn)
        except OSError as e:
            if e.errno != 2:
                reraise(e)


@pytest.fixture(
    params=[u'This is sample data as unicode. äüöå \\',
            u'',
            u'\0',
            u'multi\nline\ninput']
)
def val(request):
    return request.param


@pytest.fixture(
    params=['utf8', 'latin1']
)
def encoding(request):
    return request.param


@pytest.yield_fixture
def tmpfile():
    tmpfd, tmpfn = tempfile.mkstemp()
    try:
        yield tmpfn
    finally:
        os.unlink(tmpfn)


@pytest.fixture
def valfile(val, tmpfile, encoding):
    with open(tmpfile, 'wb') as f:
        f.write(val.encode(encoding))
    return tmpfile


@pytest.fixture(
    params=['file', 'filename', 'unicode', 'string', 'smart_file',
            'smart_unicode', 'smart_string',
            pytest.mark.skipif("PY2")('file_no_encoding')]
)
def d(val, request, encoding, valfile):
    if request.param == 'file':
        v = I(file=open(valfile, 'rb'), encoding=encoding)
    elif request.param == 'filename':
        v = I(file=valfile, encoding=encoding)
    elif request.param == 'unicode':
        v = I(data=val, encoding=encoding)
    elif request.param == 'string':
        v = I(data=val.encode(encoding), encoding=encoding)
    elif request.param == 'smart_file':
        v = I(open(valfile, 'rb'), encoding=encoding)
    elif request.param == 'smart_unicode':
        v = I(val, encoding=encoding)
    elif request.param == 'smart_string':
        v = I(val.encode(encoding), encoding=encoding)
    elif request.param == 'file_no_encoding':
        v = I(open(valfile, 'r', encoding=encoding))
    else:
        raise RuntimeError

    v._test_req = request.param

    return v


def test_getting_contents_as_bytes_str(d, val, encoding):
    assert binary_type(d) == val.encode(encoding)


def test_getting_contents_as_unicode(d, val):
    assert text_type(d) == val


def test_getting_contents_via_read(d, val):
    assert d.read() == val


def test_getting_contents_via_binary_read(d, val, encoding):
    assert d.readb() == val.encode(encoding)


def test_write_to_filename(d, val, encoding):
    with tmpfn() as fn:
        d.save_to(fn)

        with open(fn, 'rb') as f:
            assert f.read() == val.encode(encoding)


def test_write_to_file_obj(d, val, encoding):
    with tempfile.NamedTemporaryFile() as tmp:
        d.save_to(tmp)

        tmp.seek(0)

        assert tmp.read() == val.encode(encoding)


def test_with_temp_saved(d, val, encoding):
    with d.temp_saved() as tmp:
        assert tmp.read() == val.encode(encoding)


def test_with_temp_saved_fn(d, val, encoding):
    with d.temp_saved() as tmp:
        tmp.close()
        assert open(tmp.name, 'rb').read() == val.encode(encoding)


def test_unicode_reading_incremental(d, val):
    bufsize = 4

    chunks = [c for c in iter(partial(d.read, bufsize), '')]

    assert u''.join(chunks) == val


def test_bytestring_reading_incremental(d, val, encoding):
    bufsize = 4

    chunks = [c for c in iter(partial(d.readb, bufsize), b'')]

    assert b''.join(chunks) == val.encode(encoding)


def test_readline(d, val):
    buf = StringIO(val)

    for line in buf.readlines():
        assert line == d.readline()


def test_readlines(d, val):
    buf = StringIO(val)

    assert buf.readlines() == d.readlines()


def test_close(d):
    d.close()
