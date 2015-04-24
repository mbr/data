from annotate import annotate
from decorator import FunctionMaker
from six import PY2, wraps
if PY2:
    from funcsigs import signature
else:
    from inspect import signature

from . import Data


def auto_instantiate(*classes):
    def decorator(f):
        # collect our argspec
        sig = signature(f)

        @wraps(f)
        def _(*args, **kwargs):
            bvals = sig.bind(*args, **kwargs)

            # replace with instance if desired
            for varname, val in bvals.arguments.items():
                anno = sig.parameters[varname].annotation

                if anno in classes:
                    bvals.arguments[varname] = anno(val)

            return f(*bvals.args, **bvals.kwargs)

        # create another layer by wrapping in a FunctionMaker. this is done
        # to preserve the original signature
        return FunctionMaker.create(
            f, 'return _(%(signature)s)', dict(_=_, __wrapped__=f)
        )

    return decorator


def data(*argnames):
    # make it work if given only one argument (for Python3)
    if len(argnames) == 1 and callable(argnames[0]):
        return data()(argnames[0])

    def decorator(f):
        f = annotate(**dict((argname, Data) for argname in argnames))(f)
        f = auto_instantiate(Data)(f)
        return f
    return decorator


def file_arg(argname, file_arg_suffix='_file'):
    # this function is currently undocumented, as it's likely to be deemed a
    # bad idea and be removed later
    file_arg_name = argname + file_arg_suffix

    def decorator(f):
        sig = signature(f)

        if file_arg_name in sig.parameters:
            raise ValueError('{} already has a parameter named {}'
                             .format(f, file_arg_name))

        @wraps(f)
        def _(*args, **kwargs):
            # remove file_arg_name from function list
            a_file = kwargs.pop(file_arg_name, None)

            # bind remaining arguments
            pbargs = sig.bind_partial(*args, **kwargs)

            # get data argument
            a_data = pbargs.arguments.get(argname, None)

            # if a Data object is already being passed in, use it
            # instead of creating a new instance
            if a_file is None and isinstance(a_data, Data):
                d = a_data
            else:
                # create data replacement
                d = Data(data=a_data, file=a_file)

            # replace with data instance
            pbargs.parameters[argname] = d

            # call original function with instantiated data argument
            return f(*pbargs.args, **pbargs.kwargs)
        return _
    return decorator
