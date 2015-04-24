import types

from data import Data
from data.decorators import auto_instantiate, annotate, data

import pytest


# based on https://stackoverflow.com/questions/6527633
#          /how-can-i-make-a-deepcopy-of-a-function-in-python
# fixed for python 3 support
def copy_func(f, name=None):
    return types.FunctionType(f.__code__, f.__globals__, name or f.__name__,
                              f.__defaults__, f.__closure__)


def sample_func(a, b, *c, **d):
    return (a, b, c, d)


@pytest.fixture
def decfunc_all():
    f = copy_func(sample_func)
    f = annotate(a=int, b=str)(f)
    f = auto_instantiate()(f)
    return f


@pytest.fixture
def decfunc_b():
    f = copy_func(sample_func)
    f = annotate(b=str)(f)
    f = auto_instantiate()(f)
    return f


@pytest.fixture
def decfunc_int():
    f = copy_func(sample_func)
    f = annotate(a=int, b=str)(f)
    f = auto_instantiate(int)(f)
    return f


@pytest.fixture
def decfunc_data():
    f = copy_func(sample_func)
    return data('b')(f)


def test_auto_instantiation(decfunc_all):
    assert (3, '4', (), {}) == decfunc_all(3.5, 4)


def test_partial_auto_instantiation_b(decfunc_b):
    assert (3.5, '4', (), {}) == decfunc_b(3.5, 4)


def test_partial_auto_instantiation_int(decfunc_int):
    assert (3, 4, (), {}) == decfunc_int(3.5, 4)


def test_data_decorator(decfunc_data):
    a, b, c, d = decfunc_data('hello', 'world')

    assert isinstance(b, Data)
    assert not isinstance(a, Data)
