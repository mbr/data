# coding: utf-8

import os
import tempfile

from six import text_type, binary_type, PY2
import pytest

from data import Data as I


@pytest.fixture(
    params=[u'This is sample data as unicode. äüöå \\',
            u'',
            u'\0']
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
    with open(tmpfile, 'w') as f:
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
