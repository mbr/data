__version__ = '0.2.dev1'

from contextlib import contextmanager
import os
from shutil import copyfileobj
import tempfile

from six import text_type, PY2, reraise


class Data(object):
    data = None
    text = None
    file = None
    filename = None

    def __init__(self, arg=None, encoding=None, data=None, file=None):
        self.orig_args = (arg, data, file, encoding)
        if [arg, data, file].count(None) != 2:
            raise ValueError('Must supply exactly one of data or file')

        # when given a positional argument, try to be smart
        if arg is not None:
            if hasattr(arg, 'read'):
                file = arg
            else:
                data = arg
            arg = None

        if data is not None:
            if isinstance(data, text_type):
                self.text = data
            else:
                self.data = data
        elif file is not None:
            if hasattr(file, 'read'):
                self.file = file
                if getattr(file, 'encoding', None):
                    encoding = file.encoding
            else:
                self.filename = file

        self.encoding = encoding or 'utf8'

    def __bytes__(self):
        if self.data is not None:
            return self.data

        if self.text is not None:
            return self.text.encode(self.encoding)

        if self.file is not None:
            if getattr(self.file, 'encoding', None):
                # text is open in text mode
                return self.file.read().encode(self.file.encoding)
            return self.file.read()

        if self.filename is not None:
            with open(self.filename, 'rb') as f:
                return f.read()

        raise ValueError('Broken InputData, all None.')

    def __str__(self):
        if PY2:
            return self.__bytes__()
        return self.__unicode__()

    def __unicode__(self):
        if self.text is not None:
            return self.text

        if self.file is not None and getattr(self.file, 'encoding', None):
            return self.file.read()

        return self.__bytes__().decode(self.encoding)

    def __repr__(self):
        def head(buf):
            if len(buf) < 20:
                return repr(buf)

            return repr(buf[:20]) + '...'

        cname = self.__class__.__name__

        if self.data is not None:
            return '{}(data={}, encoding={!r})'.format(
                cname, head(self.data), self.encoding,
            )

        if self.text is not None:
            return '{}(data={}, encoding={!r]})'.format(
                cname, head(self.text), self.encoding,
            )

        return '{}(file={!r}, encoding={!r})'.format(
            cname, self.file or self.filename, self.encoding,
        )

    def read(self):
        return self.__unicode__()

    def readb(self):
        return self.__bytes__()

    def save_to(self, file):
        dest = file

        if hasattr(dest, 'write'):
            # writing to a file-like
            if self.file is not None:
                copyfileobj(self.file, dest)
            elif self.filename is not None:
                with open(self.filename, 'rb') as inp:
                    copyfileobj(inp, dest)
            else:
                dest.write(self.__bytes__())
        else:
            # we do not use filesystem io to make sure we have the same
            # permissions all around
            # copyfileobj() should be efficient enough

            # destination is a filename
            with open(dest, 'wb') as out:
                return self.save_to(out)

    @contextmanager
    def temp_saved(self, bufsize=-1, suffix='', prefix='tmp', dir=None):
        tmp = tempfile.NamedTemporaryFile(
            bufsize=bufsize,
            suffix=suffix,
            prefix=prefix,
            dir=dir,
            delete=False,
        )

        try:
            self.save_to(tmp)
            tmp.flush()
            tmp.seek(0)
            yield tmp
        finally:
            try:
                os.unlink(tmp.name)
            except OSError as e:
                if e.errno != 2:
                    reraise(e)
