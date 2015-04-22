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
